import { createRoot } from 'react-dom/client';
import { ConfigProvider } from 'antd';
import './index.css';
import App from './App.tsx';
import { themeConfig } from './theme/antd.config';
import { useAuthStore } from './stores/authStore';

// Инициализация auth store
useAuthStore.getState().initialize();

createRoot(document.getElementById('root')!).render(
  <ConfigProvider theme={themeConfig}>
    <App />
  </ConfigProvider>,
);
