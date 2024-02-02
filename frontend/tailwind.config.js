const config = {
  content: ['./src/**/*.{html,js,svelte,ts}', './node_modules/flowbite-svelte/**/*.{html,js,svelte,ts}'],

  plugins: [require('flowbite/plugin')],

  darkMode: 'class',

  theme: {
    extend: {
      colors: {
        'primary': {
            '50': '#F7FBFF',
            '100': '#EDF4FC',
            '200': '#D4E2FA',
            '300': '#BCCEF7',
            '400': '#8D9CF0',
            '500': '#6060eb',
            '600': '#4E4ED4',
            '700': '#3737B0',
            '800': '#23238C',
            '900': '#131369',
            '950': '#080845'
        }
      }
    }
  }
};

module.exports = config;
