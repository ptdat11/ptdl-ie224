const colors = require("colors");

export type LogLevel = "INFO" | "SAFE" | "WARNING" | "ERROR";

class Logger {
    static info(str?: string) {
        this.log("INFO", str);
    }

    static safe(str?: string) {
        this.log("SAFE", str);
    }

    static warning(str?: string) {
        this.log("WARNING", str);
    }

    static error(str?: string) {
        this.log("ERROR", str);
    }

    static log(level: LogLevel, str?: string) {
        let datetime = new Date().toLocaleString();
        let color;
        switch (level) {
            case "INFO":
                color = colors.blue; break;
            case "WARNING":
                color = colors.yellow; break;
            case "ERROR":
                color = colors.red; break;
            case "SAFE":
                color = colors.green; break;
        }
        console.log(
            `[${colors.magenta(datetime)}][${color(level)}]: ${str}`
        ); 
    }
}

export default Logger;