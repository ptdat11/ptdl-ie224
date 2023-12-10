export async function sleep(milliseconds: number) {
    await new Promise(r => setTimeout(r, milliseconds));
}

export async function randomSleep(minMilli: number, maxMilli: number) {
    let range = maxMilli - minMilli;
    let millis = Math.random()*range + minMilli;
    await sleep(millis);
}


export function infiniteInterval() {
    setInterval(infiniteInterval, 300000);
}