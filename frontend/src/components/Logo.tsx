import { Flex } from 'antd';

export const Logo = () => {
  return (
    <Flex align="center" gap={4}>
      {/* SVG Иконка из logo.svg */}
      <div style={{ 
        width: 52,
        height: 52,
        flexShrink: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}>
        <img 
          src="/logo.svg" 
          alt="AutoOffer" 
          style={{ 
            width: '90%',
            height: '90%',
            objectFit: 'contain',
            display: 'block',
          }} 
        />
      </div>

      {/* Текст */}
      <div style={{ display: 'flex', alignItems: 'center', lineHeight: 1, userSelect: 'none', marginLeft: 4 }}>
        <span
          style={{
            fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
            fontSize: '24px',
            fontWeight: 700,
            color: '#2563eb',
            letterSpacing: '-0.03em',
          }}
        >
          Auto
        </span>
        <span
          style={{
            fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
            fontSize: '24px',
            fontWeight: 700,
            color: '#0f172a',
            letterSpacing: '-0.03em',
          }}
        >
          Offer
        </span>
      </div>
    </Flex>
  );
};
