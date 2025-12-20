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
        border: 'none',
        boxShadow: '0 4px 12px rgba(37, 99, 235, 0.3)',
        transition: 'all 0.2s ease',
        ...style,
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-1px)';
        e.currentTarget.style.boxShadow = '0 6px 20px rgba(37, 99, 235, 0.4)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = '0 4px 12px rgba(37, 99, 235, 0.3)';
      }}
    >
      {children}
    </Button>
  );
};
