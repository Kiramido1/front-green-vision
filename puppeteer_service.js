/**
 * Puppeteer PDF Generation Service for Green Vision
 * Provides pixel-perfect PDF rendering using headless Chrome
 * 
 * Usage:
 * node puppeteer_service.js
 * 
 * Then call from Django:
 * POST http://localhost:3000/generate-pdf
 */

const express = require('express');
const puppeteer = require('puppeteer');
const fs = require('fs').promises;
const path = require('path');

const app = express();
const PORT = 3000;

app.use(express.json({ limit: '50mb' }));

// Generate PDF from HTML
app.post('/generate-pdf', async (req, res) => {
    let browser;
    
    try {
        const { html, filename, options = {} } = req.body;
        
        if (!html) {
            return res.status(400).json({ error: 'HTML content is required' });
        }
        
        // Launch browser
        browser = await puppeteer.launch({
            headless: 'new',
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        
        const page = await browser.newPage();
        
        // Set content
        await page.setContent(html, {
            waitUntil: 'networkidle0'
        });
        
        // Generate PDF
        const pdfOptions = {
            format: 'A4',
            printBackground: true,
            margin: {
                top: '20mm',
                right: '15mm',
                bottom: '20mm',
                left: '15mm'
            },
            ...options
        };
        
        const pdf = await page.pdf(pdfOptions);
        
        // Save to file if filename provided
        if (filename) {
            const outputPath = path.join(__dirname, 'media', 'reports', filename);
            await fs.mkdir(path.dirname(outputPath), { recursive: true });
            await fs.writeFile(outputPath, pdf);
        }
        
        await browser.close();
        
        // Return PDF as base64
        res.json({
            success: true,
            pdf: pdf.toString('base64'),
            filename: filename
        });
        
    } catch (error) {
        console.error('PDF generation error:', error);
        
        if (browser) {
            await browser.close();
        }
        
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Health check
app.get('/health', (req, res) => {
    res.json({ status: 'ok', service: 'puppeteer-pdf-service' });
});

app.listen(PORT, () => {
    console.log(`🚀 Puppeteer PDF Service running on http://localhost:${PORT}`);
    console.log(`📄 Ready to generate PDFs`);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
    console.log('SIGTERM received, shutting down gracefully');
    process.exit(0);
});
