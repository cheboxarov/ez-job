import { Flex } from 'antd';

export const Logo = () => {
  return (
    <Flex align="center" gap={8}>
      {/* SVG Иконка из logo.svg */}
      <div style={{ 
        width: 96,
        height: 96,
        flexShrink: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}>
        <img 
          src="/logo.svg" 
          alt="AutoOffer" 
          style={{ 
            width: '70%',
            height: '70%',
            objectFit: 'contain',
            display: 'block',
          }} 
        />
      </div>

      {/* Текст */}
      <div style={{ display: 'flex', alignItems: 'center', lineHeight: 1, userSelect: 'none' }}>
        <span
          style={{
            fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
            fontSize: '26px',
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
            fontSize: '26px',
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
