# Kinetic Energy Consulting website

Static site for www.kinetic-energy.co.uk, hosted on Netlify. Plain HTML, one stylesheet and one small script. No build step.

- `assets/css/site.css`: all styles. Same design language as the UK Solar Calculator and Half Hourly Insights sites.
- `assets/js/site.js`: mobile menu, dropdowns and the contact form (Formspree).
- `assets/img/`: images in WebP and JPG at 1600px and 800px.
- `assets/fonts/`: Schibsted Grotesk, self-hosted (SIL Open Font License).
- `insight/`: articles.
- `netlify.toml`: redirects for clean URLs and old Squarespace paths.

The header and footer are repeated on every page. If you change one, change them all (a find and replace across `*.html` and `insight/*.html`).
