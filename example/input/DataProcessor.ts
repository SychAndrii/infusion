import * as fs from 'fs';
import { promisify } from 'util';

const readFile = promisify(fs.readFile);

interface Data {
    id: number;
    value: number;
}

// Async function to read and process JSON data
async function processData(): Promise<Data[]> {
    try {
        const rawData = await readFile('data.json', 'utf8');
        const jsonData: Data[] = JSON.parse(rawData);

        // Process and filter data
        const filteredData = jsonData.filter(data => data.value > 100);
        return filteredData;

    } catch (error) {
        console.error('Error processing data:', error);
        throw error;
    }
}

// Main function with async/await to process data
(async function main() {
    try {
        const processedData = await processData();
        console.log('Processed Data:', processedData);
    } catch (error) {
        console.error('Main processing error:', error);
    }
})();