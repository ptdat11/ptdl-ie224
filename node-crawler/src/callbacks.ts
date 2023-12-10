import { Page } from "puppeteer";
import { PageHandler } from "./rule";
import { BatdongsanVnComItem, propertyNameMap } from "./batdongsan-com-vn-item";

const parseBatdongsanComVnItem: PageHandler = async (page: Page) => {
    const [publish, due, newsRank, id] = await page.$$eval(
        "div.js__pr-config-item:nth-of-type(n) span:last-child",
        mdata => mdata.map(el => el.textContent ?? "")
    ) as string[];

    let title = await page.$eval(
        "h1", 
        el => el.textContent
    ) as string;

    let verified = await page.$(".re__icon-verified--sm") !== null

    const [businessForm, city, district, newsInfo] = await page.$$eval(
        "div.re__breadcrumb a:nth-of-type(n)",
        item => item.map(i => i.textContent)
    ) as string[];

    const [category, street] = (/^(.+)\stại\s(.+)/.exec(newsInfo) as string[]).splice(1, 3);

    const description = await page.$eval(
        "div.re__detail-content",
        el => el.textContent ?? ""
    );

    const projectElement = await page.$("div.js__project-card-section-body");
    let projectTitle = "",
        projectPriceOnArea = "",
        projectArea = "",
        projectBuildings: string | number = "",
        projectInvestor = "";
    if (projectElement) {
        projectTitle = await projectElement.$eval(
            "div.re__project-title",
            el => el.textContent ?? ""
        );
        try {
            projectPriceOnArea = await projectElement.$eval(
                "i.re__icon-money--sm",
                el => el.nextSibling?.textContent ?? ""
            );
        } catch {
            projectPriceOnArea = "";
        }

        try {
            projectArea = await projectElement.$eval(
                "i.re__icon-size--sm",
                el => el.nextSibling?.textContent ?? ""
            );
        } catch {
            projectArea = "";
        }

        try {
            projectBuildings = await projectElement.$eval(
                "i.re__icon-building--sm",
                el => {
                    let val = el.nextSibling?.textContent;
                    return val ? Number(val) : ""
                }
            );
        } catch {
            projectBuildings = "";
        }

        projectInvestor = await projectElement.$eval(
            "i.re__icon-office--sm",
            el => el.nextSibling?.textContent ?? ""
        );
    }

    // const IQRElement = await page.$("div.pd-pricing-insight");
    // await IQRElement?.scrollIntoView();
    // await sleep(10000);
    // let IQRDomain: string = "",
    //     IQR_Q1: string = "", 
    //     IQR_Q2: string = "", 
    //     IQR_Q3: string = "";
    // if (IQRElement) {
    //     IQRDomain = await page.$eval(
    //         "div.pricing-insight--sub-title",
    //         el => {
    //             if (!el.textContent) return "";
    //             const regex = /.+tại\s(.+)$/.exec(el.textContent)
    //             return regex ? regex[1] : ""
    //     });
    //     IQR_Q1 = await IQRElement.$eval(
    //         "div.pricing-avg-min div div div:last-child",
    //         el => el.textContent ?? ""
    //     );
    //     IQR_Q2 = await IQRElement.$eval(
    //         "div.pricing-avg div div div:last-child",
    //         el => el.textContent ?? ""
    //     );
    //     IQR_Q3 = await IQRElement.$eval(
    //         "div.pricing-avg-max div div div:last-child",
    //         el => el.textContent ?? ""
    //     );
    // }

    let mapSrc = "";
    try {
        mapSrc = await page.$eval(
            "iframe.lazyload",
            ifr => ifr.getAttribute("data-src") ?? ""
        );
    } catch {
        mapSrc = await page.$eval(
            "iframe.lazyloaded",
            ifr => ifr.getAttribute("data-src") ?? ""
        );
    }
    const [latitude, longitude] = (
        /.*q=\s*?([0-9\.]+),([0-9\.]+).*/.
            exec(mapSrc) as string[]
        ).splice(1, 3);
    
    const items = await page.$$("div.re__pr-specs-content-item")
    let ps = await Promise.all(await items.map(
        async handle => {
            let key = await handle.$eval(
                "span:nth-of-type(2)",
                el => el.textContent ?? ""
            );
            let value = await handle.$eval(
                "span:nth-of-type(3)",
                el => el.textContent ?? ""
            );
            return {
                key: propertyNameMap[key],
                value: value
            };
        }
    ));
    const properties: { [key: string]: string | number } = {};
    for (const property of ps) {
        properties[property.key] = property.value;
    }

    const result: BatdongsanVnComItem = {
        _id: Number(id),
        title: title.trim(),
        url: page.url(),
        verified: verified,
        publishDate: publish.trim(),
        dueDate: due.trim(),
        newsRank: newsRank.trim(),
        businessForm: businessForm.trim(),
        city: city.trim(),
        district: district.trim(),
        street: street.trim(),
        category: category.trim(),
        description: description.trim(),
        projectTitle: projectTitle.trim(),
        projectPriceOnArea: projectPriceOnArea.trim(),
        projectArea: projectArea.trim(),
        projectBuildings: projectBuildings,
        projectInvestor: projectInvestor.trim(),
        // IQRDomain: IQRDomain,
        // IQR_Q1: IQR_Q1.trim(),
        // IQR_Q2: IQR_Q2.trim(),
        // IQR_Q3: IQR_Q3.trim(),
        latitude: Number(latitude),
        longitude: Number(longitude),
        area: properties["area"] as string,
        price: properties["price"] as string,
        frontLength: properties["frontLength"] as string,
        entranceLength: properties["entranceLength"] as string,
        facingDir: properties["facingDir"] as string,
        balconyDir: properties["balconyDir"] as string,
        floor: properties["floor"] ? 
            Number(properties["floor"].toString().split(" ")[0]) : 
            undefined,
        bedroom: properties["bedroom"] ? 
            Number(properties["bedroom"].toString().split(" ")[0]) :
            undefined,
        wc: properties["wc"] ? 
            Number(properties["wc"].toString().split(" ")[0]) :
            undefined,
        legalStatus: properties["legalStatus"] as string,
        furniture: properties["furniture"] as string
    }
    return result;
};

export {parseBatdongsanComVnItem};