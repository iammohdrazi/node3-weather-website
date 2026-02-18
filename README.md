# Node.js Weather Website

A simple weather application built with Node.js, Express, and Handlebars that provides real-time weather information for any location.

## Features

- Get current weather data for any address
- Clean, responsive web interface
- Error handling for invalid addresses
- Multiple pages (Home, About, Help)
- 404 error handling

## Technologies Used

- **Node.js** - JavaScript runtime
- **Express.js** - Web framework
- **Handlebars (hbs)** - Template engine
- **Postman Request** - HTTP client for API calls

## Prerequisites

- Node.js (v12 or higher)
- npm (comes with Node.js)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd node3-weather-website
```

2. Install dependencies:
```bash
npm install
```

## Usage

1. Start the server:
```bash
npm start
```

2. Open your browser and navigate to:
```
http://localhost:3000
```

3. Enter an address in the search field to get weather information

## API Endpoints

- `GET /` - Home page
- `GET /about` - About page
- `GET /help` - Help page
- `GET /weather?address=<location>` - Get weather data for a specific address
- `GET /product?search=<term>` - Product search endpoint
- `GET *` - 404 error handling

## Project Structure

```
node3-weather-website/
├── public/                 # Static assets
├── src/                   # Source files
│   ├── app.js            # Main application file
│   └── utils/            # Utility functions
│       ├── geocode.js    # Location geocoding
│       └── forecast.js   # Weather data fetching
├── templates/             # Handlebars templates
│   ├── views/            # Main page templates
│   └── partials/         # Reusable template parts
├── package.json          # Project dependencies
└── README.md            # This file
```

## Environment Variables

- `PORT` - Server port (defaults to 3000)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Commit your changes
5. Push to the branch
6. Create a Pull Request

## Author

**Mohammad Razi**

## License

This project is licensed under the ISC License.

## Support

For support, please contact: zaphlabsInc@gmail.com
