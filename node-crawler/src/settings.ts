import { PuppeteerLaunchOptions } from "puppeteer";
import Rule from "./rule";
import { parseBatdongsanComVnItem } from "./callbacks";
import { CsvPipeline, LogItemPipeline } from "./pipeline-processors";
import { PipelineItemProcessor } from "./base-classes";

class CrawlerSettings {
        static startUrls: string[] = [
        "https://batdongsan.com.vn/nha-dat-ban?vrs=1",
        "https://batdongsan.com.vn/nha-dat-cho-thue?vrs=1"
        // "https://batdongsan.com.vn/nha-dat-ban/p1",
        // "https://batdongsan.com.vn/nha-dat-cho-thue/p1"
    ]

    static rules: Rule[] = [
        new Rule({
            allow: "(/p[0-9]+)?\\?vrs=1$",
            // allow: "/p[0-9]+$",
            follow: true
        }),
        new Rule({
            allow: "-pr[0-9]+$",
            follow: false,
            pageHandler: parseBatdongsanComVnItem
        })
    ];

    static browserLaunchOptions: PuppeteerLaunchOptions = {
        headless: "new",
        // executablePath: "/usr/bin/google-chrome",
        args: ['--disable-features=site-per-process']
    };

    static randomSleepDurationDomain: [number, number] = [7, 10];

    static skipImageRequests: boolean = true;

    static progressHistoryDirectory: string = `${__dirname}/../history`
}

class PipelineSettings {
    static processors: PipelineItemProcessor[] = [
        new LogItemPipeline(),
        new CsvPipeline(),
    ];
}

export {CrawlerSettings, PipelineSettings};