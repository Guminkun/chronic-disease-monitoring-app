/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 主色调 - 清新蓝色
        primary: {
          50: '#EFF6FF',
          100: '#DBEAFE',
          200: '#BFDBFE',
          300: '#93C5FD',
          400: '#60A5FA',
          500: '#3B82F6',
          600: '#2563EB',
          700: '#1D4ED8',
        },
        // 次要色 - 柔和灰蓝
        secondary: {
          50: '#F8FAFC',
          100: '#F1F5F9',
          200: '#E2E8F0',
          300: '#CBD5E1',
          400: '#94A3B8',
          500: '#64748B',
        },
        // 成功色 - 清新绿色
        success: {
          50: '#F0FDF4',
          100: '#DCFCE7',
          200: '#BBF7D0',
          500: '#22C55E',
          600: '#16A34A',
        },
        // 警告色 - 温暖橙色
        warning: {
          50: '#FFF7ED',
          100: '#FFEDD5',
          500: '#F97316',
          600: '#EA580C',
        },
        // 危险色 - 柔和红色
        danger: {
          50: '#FEF2F2',
          100: '#FEE2E2',
          500: '#EF4444',
          600: '#DC2626',
        },
        // 背景色
        background: '#F8FAFC',
        surface: '#FFFFFF',
        // 侧边栏 - 明亮风格
        sidebar: {
          bg: '#FFFFFF',
          text: '#64748B',
          active: '#3B82F6',
          hover: '#F1F5F9',
          border: '#E2E8F0',
        },
        // 卡片背景色
        card: {
          blue: '#EFF6FF',
          green: '#F0FDF4',
          purple: '#FAF5FF',
          orange: '#FFF7ED',
          pink: '#FDF2F8',
        },
        // 文字颜色
        text: {
          primary: '#1E293B',
          secondary: '#64748B',
          muted: '#94A3B8',
        }
      },
      fontFamily: {
        sans: [
          'Noto Sans SC',
          'Figtree',
          'Noto Sans',
          'system-ui',
          '-apple-system',
          'Segoe UI',
          'PingFang SC',
          'Hiragino Sans GB',
          'Microsoft YaHei',
          'Helvetica',
          'Arial',
          'sans-serif',
        ],
      },
      boxShadow: {
        'card': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        'card-hover': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'sidebar': '2px 0 8px 0 rgba(0, 0, 0, 0.05)',
      },
      borderRadius: {
        'xl': '0.75rem',
        '2xl': '1rem',
      },
    },
  },
  plugins: [],
}
