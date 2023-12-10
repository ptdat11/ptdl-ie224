import { CrawledItem } from "./batdongsan-com-vn-item";

export abstract class PipelineItemProcessor {
    abstract processItem(item: CrawledItem): CrawledItem;
}