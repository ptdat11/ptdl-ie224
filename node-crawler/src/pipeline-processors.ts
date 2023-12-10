import { stringify } from "csv"
import fs from "fs"
import { CrawledItem } from "./batdongsan-com-vn-item"
import { PipelineItemProcessor } from "./base-classes"
import Logger from "./logger";

export class CsvPipeline extends PipelineItemProcessor {
    static header: boolean = false;

    processItem(item: CrawledItem) {
        stringify(
            [item], 
            {
                header: CsvPipeline.header
            }, 
            (err, output) => fs.appendFile(
                `${__dirname}/batdongsan_com_vn.csv`, 
                output, 
                () => Logger.error(err?.message)
        ));

        if (CsvPipeline.header) {
            CsvPipeline.header = false;
        }

        return item
    }
}

export class LogItemPipeline extends PipelineItemProcessor {
    processItem(item: CrawledItem): CrawledItem {
        let out = JSON.stringify(item);
        console.log(out);

        return item;
    }
}