import React, { useState, useEffect, useRef } from "react";

interface Image {
  src: string;
  alt: string;
  caption: string;
}

interface ModernFadeSliderProps {
  images: Image[];
  interval?: number;
}

const FADE_DURATION = 1000; // ms

const ModernFadeSlider: React.FC<ModernFadeSliderProps> = ({
  images,
  interval = 4000,
}) => {
  const [current, setCurrent] = useState(0);
  const [fade, setFade] = useState(true);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const [paused, setPaused] = useState(false);

  useEffect(() => {
    if (!paused) {
      timeoutRef.current = setTimeout(() => {
        setFade(false);
        setTimeout(() => {
          setCurrent((prev) => (prev + 1) % images.length);
          setFade(true);
        }, FADE_DURATION); // fade out duration
      }, interval);
    }
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, [current, paused, interval, images.length]);

  const goTo = (idx: number) => {
    setFade(false);
    setTimeout(() => {
      setCurrent(idx);
      setFade(true);
    }, FADE_DURATION);
    setPaused(true);
  };

  const prev = () => {
    setFade(false);
    setTimeout(() => {
      setCurrent((prev) => (prev - 1 + images.length) % images.length);
      setFade(true);
    }, FADE_DURATION);
    setPaused(true);
  };
  const next = () => {
    setFade(false);
    setTimeout(() => {
      setCurrent((prev) => (prev + 1) % images.length);
      setFade(true);
    }, FADE_DURATION);
    setPaused(true);
  };

  return (
    <div className="relative w-full flex flex-col items-center select-none">
      <div
        className="w-full h-[500px] flex flex-col items-center justify-center overflow-hidden bg-white rounded-xl shadow-lg relative"
        onMouseEnter={() => setPaused(true)}
        onMouseLeave={() => setPaused(false)}
      >
        {images.map((img, idx) => (
          <React.Fragment key={idx}>
            <img
              src={img.src}
              alt={img.alt}
              className={`absolute top-0 left-0 w-full h-full object-cover transition-opacity duration-[1000ms] ease-in-out ${idx === current && fade ? "opacity-100 z-10" : "opacity-0 z-0"}`}
              style={{ transition: "opacity 1s cubic-bezier(0.4,0,0.2,1)" }}
              draggable={false}
            />
            <figcaption
              className={`absolute bottom-0 left-0 w-full text-white text-center text-base py-2 px-4 rounded-b-xl bg-black/60 transition-opacity duration-[1000ms] ease-in-out ${idx === current && fade ? "opacity-100 z-20" : "opacity-0 z-0"}`}
              style={{ transition: "opacity 1s cubic-bezier(0.4,0,0.2,1)" }}
            >
              {img.caption || img.alt}
            </figcaption>
          </React.Fragment>
        ))}
      </div>
      {/* Controles */}
      <div className="flex items-center gap-4 mt-4">
        <button
          aria-label="Anterior"
          onClick={prev}
          className="p-2 rounded-full bg-congress-blue hover:bg-congress-blue-dark text-white text-2xl"
        >
          &#8592;
        </button>
        <div className="flex gap-1">
          {images.map((_, idx) => (
            <button
              key={idx}
              className={`w-3 h-3 rounded-full ${idx === current ? "bg-congress-cyan" : "bg-gray-300"}`}
              onClick={() => goTo(idx)}
              aria-label={`Ir a la imagen ${idx + 1}`}
            />
          ))}
        </div>
        <button
          aria-label="Siguiente"
          onClick={next}
          className="p-2 rounded-full bg-congress-blue hover:bg-congress-blue-dark text-white text-2xl"
        >
          &#8594;
        </button>
      </div>
    </div>
  );
};

export default ModernFadeSlider;