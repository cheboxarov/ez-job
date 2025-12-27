import { createRoot } from 'react-dom/client';
import { ConfigProvider } from 'antd';
import { HelmetProvider } from 'react-helmet-async';
import './index.css';
import App from './App.tsx';
import { themeConfig } from './theme/antd.config';
import { useAuthStore } from './stores/authStore';

// Инициализация auth store
useAuthStore.getState().initialize();

createRoot(document.getElementById('root')!).render(
  <HelmetProvider>
    <ConfigProvider theme={themeConfig}>
      <App />
    </ConfigProvider>
  </HelmetProvider>,
);
