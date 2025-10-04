/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      fontFamily: {
        'orbitron': ['Orbitron', 'monospace'],
        'poppins': ['Poppins', 'sans-serif'],
      },
      colors: {
        'neon-green': '#00ff88',
        'neon-teal': '#00ffff',
        'neon-cyan': '#00e6ff',
        'eco-green': '#4ade80',
        'dark-bg': '#0a0a0a',
        'dark-secondary': '#1a1a1a',
        'dark-accent': '#2a2a2a',
      },
      animation: {
        'fade-in-up': 'fadeInUp 1s ease-out forwards',
        'fade-in-up-delay': 'fadeInUp 1s ease-out 0.3s forwards',
        'fade-in-up-delay-2': 'fadeInUp 1s ease-out 0.6s forwards',
        'glow-pulse': 'glowPulse 2s ease-in-out infinite alternate',
        'float': 'float 6s ease-in-out infinite',
        'rotate-slow': 'rotateSlow 20s linear infinite',
      },
      keyframes: {
        fadeInUp: {
          '0%': {
            opacity: '0',
            transform: 'translateY(30px)'
          },
          '100%': {
            opacity: '1',
            transform: 'translateY(0)'
          }
        },
        glowPulse: {
          '0%': {
            boxShadow: '0 0 20px rgba(0, 255, 136, 0.5)'
          },
          '100%': {
            boxShadow: '0 0 40px rgba(0, 255, 136, 0.8), 0 0 60px rgba(0, 255, 136, 0.4)'
          }
        },
        float: {
          '0%, 100%': {
            transform: 'translateY(0px)'
          },
          '50%': {
            transform: 'translateY(-20px)'
          }
        },
        rotateSlow: {
          '0%': {
            transform: 'rotate(0deg)'
          },
          '100%': {
            transform: 'rotate(360deg)'
          }
        }
      },
      backdropBlur: {
        'xs': '2px',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'eco-gradient': 'linear-gradient(135deg, #00ff88, #00ffff)',
        'dark-gradient': 'linear-gradient(135deg, #111827, #000000)',
      }
    },
  },
  plugins: [],
}




