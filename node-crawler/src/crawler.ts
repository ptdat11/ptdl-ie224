import puppeteer, { Browser, Page } from "puppeteer";
import Rule from "./rule";
import { Queue } from "typescript-queue";
import { CrawlerSettings } from "./settings";
import { randomSleep, sleep } from "./utils";
import Logger from "./logger";
import Pipeline from "./pipeline";
import ProgressHistory from "./progress-history";
import LinkExtractor from "./link-extractor";
const colors = require("colors");

class Crawler {
    browser?: Browser;
    rules: Rule[] = CrawlerSettings.rules;
    propagatedUrls: Set<string> = new Set(
        ProgressHistory.loadPropagatedUrls()
    );
    private propagationQueue: Queue<string>;

    constructor (startUrls: string[] = CrawlerSettings.startUrls) {
        const historyQueue = ProgressHistory.loadQueue();
        const queue = historyQueue.length == 0 ?
            startUrls :
            historyQueue;
        this.propagationQueue = new Queue(queue);
    }

    async launchBrowser() {
        this.browser = await puppeteer.launch(CrawlerSettings.browserLaunchOptions);
        return this.browser;
    }

    async start() {
        Logger.info("Crawler started");
        
        for (
            let url = this.propagationQueue.poll();
            url;
            url = this.propagationQueue.poll()
        ) {
            try {
                if (this.propagatedUrls.has(url)) {
                    continue;
                }
    
                const [page, browser] = await this.goTo(url);
                this.propagatedUrls.add(url);

                LinkExtractor
    
                for (const rule of this.rules) {
                    if (rule.match(url)) {
                        await this.handleRule(rule, page);
                    }
                }
    
                // await browser.close();
                ProgressHistory.savePropagatedUrls(this.propagatedUrls);
                ProgressHistory.saveQueue(this.propagationQueue);

                await this.sleep();
            } catch (e) {
                let err: Error = e as Error;
                Logger.error(`${err.name}: ${err.message}`);
                Logger.error(err.stack);
                continue;
            } finally {
                await this.browser?.close();
            }
            Logger.info(`There are ${this.propagationQueue.size()} URLs to be examined`);
        }
    }

    async goTo(url: string) {
        const browser = await this.launchBrowser();
        const page = (await browser.pages())[0];
        const response = await page.goto(url, {timeout: 0});
        await this.setRequestInterception(page, CrawlerSettings.skipImageRequests);
        Logger.info(`GET ${response?.status()} ${response?.statusText()}: ${colors.green(url)}`)
        
        const result: [Page, Browser] = [page, browser];
        return result;
    }

    async handleRule(rule: Rule, page: Page) {
        if (!page)
            return;

        if (rule.follow) {
            await this.executeFollow(page);
        }
        if (rule.handler) {
            let item = await rule.handler(page);
            item = Pipeline.process(item);
        }
    }

    private async executeFollow(page: Page) {
        for (let rule of this.rules) {
            const hrefs = await rule.extractor.extract(page);

            const unpropagatedHrefs = hrefs.filter(
                href => !this.propagatedUrls.has(href) &&
                !href.startsWith("mailto:")
            );
            this.propagationQueue.add(unpropagatedHrefs);
        }
    }

    private async setRequestInterception(page: Page, bool: boolean) {
        await page.setRequestInterception(bool);
        if (!bool)
            return;

        page.on("request", async (req) => {
            if (
                !["document", "xhr", "fetch", "script"].includes(req.resourceType())
            ) {
                // Logger.info(`Aborted ${colors.green(req.url())}`)
                await req.abort();
                return;
            }
            // Logger.info(`Fetched ${colors.green(req.resourceType())}`)
            await req.continue();
        });
    }

    async sleep() {
        const [min, max] = CrawlerSettings.randomSleepDurationDomain;
        await randomSleep(min*1000, max*1000);
    }

    async delay(millisecond: number) {
        await sleep(millisecond);
    }
}

export default Crawler;