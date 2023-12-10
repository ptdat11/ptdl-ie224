import { Page } from "puppeteer";
import LinkExtractor from "./link-extractor";
import { CrawledItem } from "./batdongsan-com-vn-item";

export type PageHandler = (page: Page) => Promise<CrawledItem>;

class Rule {
    extractor: LinkExtractor;
    follow: boolean;
    handler: PageHandler | undefined;

    constructor (args: {
        allow?: string,
        deny?: string,
        follow?: boolean,
        pageHandler?: PageHandler
    }) {
        this.extractor = new LinkExtractor({
            allow: args.allow,
            deny: args.deny
        });
        this.follow = args.follow ? args.follow : true;
        this.handler = args.pageHandler;
    }

    match(url: string) {
        let allow = this.extractor.allow;
        let deny = this.extractor.deny;

        if (!allow && !deny) {
            return true;
        }

        const allowRegex = allow ? new RegExp(allow) : undefined;
        const denyRegex = deny ? new RegExp(deny) : undefined;

        let matched = allowRegex?.test(url) && !denyRegex?.test(url);
        return matched;
    }
}

export default Rule;