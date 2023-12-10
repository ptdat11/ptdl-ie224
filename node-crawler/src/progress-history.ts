import { Queue } from "typescript-queue";
import Logger from "./logger";
import { CrawlerSettings } from "./settings"
import fs from "fs"

class ProgressHistory {
    static historyDir: string = CrawlerSettings.progressHistoryDirectory.endsWith("/") ?
        CrawlerSettings.progressHistoryDirectory :
        CrawlerSettings.progressHistoryDirectory + "/";
    static propagatedFileName = "propagated.history";
    static queueFileName = "queue.history";

    static loadPropagatedUrls() {
        return ProgressHistory.readStringArr(
            ProgressHistory.propagatedFileName
        );
    }

    static loadQueue() {
        return ProgressHistory.readStringArr(
            ProgressHistory.queueFileName
        );
    }

    static savePropagatedUrls(set: Set<string>) {
        ProgressHistory.writeStringArr(
            [...set.keys()], 
            ProgressHistory.propagatedFileName
        );
    }

    static saveQueue(queue: Queue<string>) {
        ProgressHistory.writeStringArr(
            queue.toArray(),
            ProgressHistory.queueFileName
        );
    }

    private static writeStringArr(arr: string[], fileName: string) {
        let path = ProgressHistory.historyDir + fileName;
        fs.writeFileSync(path, JSON.stringify(arr));
    }

    private static readStringArr(fileName: string) {
        let path = ProgressHistory.historyDir + fileName;
        if (!fs.existsSync(path))
            fs.writeFileSync(path, "[]");

        let history: string = fs.readFileSync(path).toString();
        return JSON.parse(history) as string[];
    }
}

export default ProgressHistory;