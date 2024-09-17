import * as fs from 'fs';
import { promisify } from 'util';

const readFile = promisify(fs.readFile);

/**
 * Interface for the Data object.
 * @interface
 * @property {number} id - The id of the data.
 * @property {number} value - The value of the data.
 */
interface Data {
    id: number;
    value: number;
}

/**
 * Asynchronously reads and processes JSON data from a file.
 * Filters out Data objects with a value less than or equal to 100.
 * @async
 * @function
 * @returns {Promise<Data[]>} - A promise that resolves to an array of Data objects.
 * @throws Will throw an error if reading the file or processing the data fails.
 */
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

/**
 * Main function that initiates data processing.
 * Logs the processed data or any errors to the console.
 * @async
 * @function
 */
(async function main() {
    try {
        const processedData = await processData();
        console.log('Processed Data:', processedData);
    } catch (error) {
        console.error('Main processing error:', error);
    }
})();