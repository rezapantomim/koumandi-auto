import React from 'react';
import { AbsoluteFill, Img, OffthreadVideo, staticFile } from 'remotion';
import type { Props } from './types';
import { HEAD } from './fonts';

/** 1280x720 thumbnail: topic picture / own Short in the background, huge Persian headline on the right (RTL), brand badge. */
export const Thumb: React.FC<Props> = (p) => {
  const words = p.thumbText.split(' ');
  const hl = p.thumbHighlight || '';
  const size = words.length > 3 ? 130 : 160;
  return (
    <AbsoluteFill style={{ background: p.style.bg, overflow: 'hidden', direction: 'rtl' }}>
      {p.thumbClip ? (
        <AbsoluteFill style={{ opacity: 0.6 }}>
          <OffthreadVideo src={staticFile(p.thumbClip)} muted style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
        </AbsoluteFill>
      ) : p.thumbImg ? (
        <AbsoluteFill style={{ opacity: 0.65 }}>
          <Img src={staticFile(p.thumbImg)} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
        </AbsoluteFill>
      ) : (
        <AbsoluteFill style={{ background: `radial-gradient(circle at 25% 60%, ${p.style.accent2}55 0%, ${p.style.bg} 60%)` }} />
      )}
      <AbsoluteFill style={{ background: `linear-gradient(270deg, ${p.style.bg} 0%, ${p.style.bg}cc 45%, #0000 100%)` }} />

      <div style={{ position: 'absolute', right: 70, top: 80, width: 900, fontFamily: HEAD, fontWeight: 900, fontSize: size, lineHeight: 1.15,
        color: p.style.text, textShadow: '0 8px 24px #000', textAlign: 'right' }}>
        {words.map((w, i) => (
          <span key={i} style={{ color: hl && hl.includes(w) ? p.style.accent : p.style.text }}>{w} </span>
        ))}
      </div>
      <div style={{ position: 'absolute', right: 70, bottom: 56, display: 'flex', gap: 16 }}>
        <div style={{ background: p.style.accent, color: p.style.bg, fontFamily: HEAD, fontWeight: 900, fontSize: 44, padding: '4px 22px',
          borderRadius: 12, direction: 'ltr' }}>KOUMANDI</div>
      </div>
      <div style={{ position: 'absolute', right: 0, top: 0, bottom: 0, width: 18, background: p.style.accent }} />
    </AbsoluteFill>
  );
};
