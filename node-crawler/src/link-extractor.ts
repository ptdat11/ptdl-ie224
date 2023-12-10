import { Page } from "puppeteer";

class LinkExtractor {
    allow: string | undefined;
    deny: string | undefined

    constructor (args: {
        allow?: string,
        deny?: string
    }) {
        this.allow = args.allow;
        this.deny = args.deny;
    }

    async extract(page: Page) {
        const hrefs = await page.$$eval(
            "a", 
            anchors => anchors.map(a => a.href)
        );
        if (!this.allow && !this.deny)
            return hrefs;

        let allowRegex = this.allow ? RegExp(this.allow) : undefined
        let denyRegex = this.deny ? RegExp(this.deny) : undefined

        const matches = hrefs.filter(
            href => allowRegex?.test(href) && !denyRegex?.test(href)
        );
        return matches;
    }
}

export default LinkExtractor;