import { PipelineItemProcessor } from "./base-classes";
import { CrawledItem } from "./batdongsan-com-vn-item"
import { PipelineSettings } from "./settings"

class Pipeline {
    static processors: PipelineItemProcessor[] = PipelineSettings.processors;

    static process(item: CrawledItem) {
        for (const processor of this.processors) {
            item = processor.processItem(item);
        }
        return item;
    }
}

export default Pipeline;