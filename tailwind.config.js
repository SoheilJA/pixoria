/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.html", "./static/src/**/*.js"],
  theme: {
    extend: {
      backgroundImage: {
        "gradient-radial": "radial-gradient(circle, var(--tw-gradient-stops))",
      },
      colors: {
        gray: {
          25: "#f8f8f8",
        },
      },
    },
  },
  plugins: [],
};
