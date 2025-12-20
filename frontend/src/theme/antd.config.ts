import type { ThemeConfig } from 'antd';

export const themeConfig: ThemeConfig = {
  token: {
    colorPrimary: '#2563eb',
    borderRadius: 16,
    fontFamily: 'Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    colorText: '#111827',
    colorTextSecondary: '#6b7280',
    colorBgContainer: '#ffffff',
    colorBgBase: '#f3f4f6',
    colorBorder: '#e5e7eb',
    fontSize: 14,
  },
  components: {
    Card: {
      borderRadius: 20,
      paddingLG: 24,
      boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.03)',
    },
    Button: {
      borderRadius: 12,
      controlHeight: 40,
      controlHeightLG: 48,
      fontWeight: 600,
      defaultShadow: 'none',
      primaryShadow: '0 4px 6px -1px rgba(37, 99, 235, 0.2), 0 2px 4px -1px rgba(37, 99, 235, 0.1)',
    },
    Input: {
      borderRadius: 12,
      controlHeight: 44,
    },
    Tag: {
      borderRadius: 8,
      fontSize: 13,
    },
    Typography: {
      fontWeightStrong: 700,
    }
  },
};

