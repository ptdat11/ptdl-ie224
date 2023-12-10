import Crawler from "./crawler"
import ProgressHistory from "./progress-history";
import { infiniteInterval } from "./utils";
import fs from "fs"

const main = async () => {
    fs.mkdir("history", () => {});
    const crawler = new Crawler();
    await crawler.start();
}

main();

// let propagated = ProgressHistory.loadPropagatedUrls()
// const pageRegex = RegExp("(/p[0-9]+)?\\?vrs=1$")
// const pages = propagated.filter(url => pageRegex.test(url))
// const notPages = propagated.filter(url => !pageRegex.test(url))
// console.log(pages.length + notPages.length, propagated.length)
// ProgressHistory.savePropagatedUrls(new Set(notPages))

infiniteInterval();