import puppeteer from "puppeteer";
import fs from "fs";

import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const dataset = [];
const datasetFile = 'dataset.json';
let previousPercentage = 0;

async function main() {
    // Load existing dataset if available
    if (fs.existsSync(datasetFile)) {
        if (IsCommandArgument("--restart-dataset")) {
            fs.unlinkSync(datasetFile);
            console.log("Dataset restart: dataset.json deleted.");
        } else {
            const data = fs.readFileSync(datasetFile);
            Object.assign(dataset, JSON.parse(data));
            console.log("Dataset loaded: ", dataset.length, " entries.");
        }
    }   

    // Check for --cleanup argument
    if(IsCommandArgument("--clean")) {
        // Delete all files in the img folder
        const dir = 'img';
        if (fs.existsSync(dir)) {
            fs.readdirSync(dir).forEach((file) => {
                fs.unlinkSync(`${dir}/${file}`);
            });
            console.log("Cleanup completed: All files in img/ deleted.");
        } else {
            console.log("No img/ directory found to clean up.");
        }
    }

    let dirname = __dirname;
    if(__dirname.startsWith("/mnt/")) {
        // Convert WSL path to Windows path
        dirname = __dirname.replace("/mnt/", "")

        const driveLetter = dirname.charAt(0);
        dirname = driveLetter.toUpperCase() + ":" + dirname.slice(1);
    }

    const browser = await puppeteer.launch();
    
    for (let i = 0; i < (GetCommandArgumentValue("--loop") || 1); i++) {
        const page = await browser.newPage();



        await page.goto(`file:///${__dirname}/captcha_generator.html`);
        
        // Read every "captcha-char" element and print its text content
        const char = await page.evaluate(() => {
            const charElements = document.querySelectorAll('.captcha-char');
            return Array.from(charElements).map(el => el.textContent).join('');
        });

        // Make an img folder if it doesn't exist
        if (!fs.existsSync('img')) {
            fs.mkdirSync('img');
        }

        // Take screenshot of the element with class "captcha-text"
        const fileElement = await page.$('.captcha-text')

        if(!fileElement) {
            throw new Error("Captcha element not found");
        }

        await fileElement.screenshot({ path: `img/${char}.png` });

        PrintPercentageBar(i, GetCommandArgumentValue("--loop") || 1);
        dataset.push({ captcha: char, image: `/img/${char}.png` });

        page.close();
    }
    
    // Save dataset to file
    fs.writeFileSync(datasetFile, JSON.stringify(dataset, null, 2));
    console.log("\nDataset saved: ", dataset.length, " entries.");

    process.exit(0);
}

export function PrintPercentageBar(i, max) {
    const percentage = ((i + 1) / max) * 100;

    if (percentage - previousPercentage < 0.5 && percentage < 100) {
        return;
    }

    previousPercentage = percentage;

    const barLength = 20;
    const filledLength = Math.round((percentage / 100) * barLength);
    const bar = '█'.repeat(filledLength) + '-'.repeat(barLength - filledLength);
    process.stdout.write(`\rProgress: |${bar}| ${percentage.toFixed(2)}%`);

}

export function IsCommandArgument(arg) {
    // Check if the arg starts with the argument
    return process.argv.slice(2).some(a => a.startsWith(arg));
}

export function GetCommandArgumentValue(arg) {
    // Find the argument that starts with the specified arg
    const argument = process.argv.slice(2).find(a => a.startsWith(arg));
    if (argument) {
        const parts = argument.split("=");
        if (parts.length === 2) {
            return parts[1];
        }
    }
    return null;
}

main();

