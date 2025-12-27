import { Button } from 'antd';
import type React from 'react';

interface GradientButtonProps extends Omit<React.ComponentProps<typeof Button>, 'type'> {
  children: React.ReactNode;
}

export const GradientButton = ({ children, style, ...props }: GradientButtonProps) => {
  return (
    <Button
      type="primary"
      {...props}
      style={{
        height: 44,
        fontSize: 15,
        fontWeight: 600,
        borderRadius: 10,
        background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
        border: '1px solid #2563eb',
        transition: 'all 0.2s ease',
        ...style,
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.borderColor = '#1d4ed8';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = '#2563eb';
      }}
    >
      {children}
    </Button>
  );
};
