const axios = require('axios');
const { JSDOM } = require('jsdom');
const { Readability } = require('@mozilla/readability');
const fs = require('fs');

// Load the API data from the JSON file
const apiData = require('./api-result.json');

// Array to store the extracted articles
let extractedArticles = [];

// Iterate over each entry in the data array
apiData.data.forEach((entry) => {
    // Fetch the HTML content of the URL
    axios.get(entry.url).then(function(response) {
        let dom = new JSDOM(response.data, {
            url: entry.url
        });

        // Parse the article content using Readability
        let article = new Readability(dom.window.document).parse();

        // Extract title and content
        let title = article.title;
        let content = article.textContent;

        // Store the URL, title, and extracted content
        extractedArticles.push({ url: entry.url, title: title, content: content });

        // Check if all URLs have been processed
        if (extractedArticles.length === apiData.data.length) {
            // Write the extracted articles to a new JSON file
            fs.writeFileSync('output/extracted_articles.json', JSON.stringify(extractedArticles, null, 2));
        }
    }).catch(function(error) {
        console.error('Error fetching or parsing the article:', error);
    });
});