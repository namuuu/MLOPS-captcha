import puppeteer from "puppeteer";
import fs from "fs";

import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function main() {
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

    const browser = await puppeteer.launch();
    
    for (let i = 0; i < (GetCommandArgumentValue("--loop") || 1); i++) {
        const page = await browser.newPage();

        await page.goto(`file:///${__dirname}/captcha_generator.html`);
        
        // Read every "captcha-char" element and print its text content
        const char = await page.evaluate(() => {
            const charElements = document.querySelectorAll('.captcha-char');
            return Array.from(charElements).map(el => el.textContent).join('');
        });

        console.log("Captcha Text:", char);

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
        console.log(`Captcha screenshot saved as img/${char}.png`);

        page.close();
    }
    

    await browser.close();
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

