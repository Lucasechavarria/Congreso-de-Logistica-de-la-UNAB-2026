import React, { useState, useEffect, useRef } from "react";

interface Image {
  src: string;
  alt: string;
  caption: string;
}

interface ImageSliderProps {
  images: Image[];
  interval?: number; // ms
}

const ImageSlider: React.FC<ImageSliderProps> = ({
  images,
  interval = 4000,
}) => {
  const [current, setCurrent] = useState(0);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const [paused, setPaused] = useState(false);

  useEffect(() => {
    if (!paused) {
      timeoutRef.current = setTimeout(() => {
        setCurrent((prev) => (prev + 1) % images.length);
      }, interval);
    }
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, [current, paused, interval, images.length]);

  const goTo = (idx: number) => {
    setCurrent(idx);
    setPaused(true);
  };

  const prev = () => {
    setCurrent((prev) => (prev - 1 + images.length) % images.length);
    setPaused(true);
  };
  const next = () => {
    setCurrent((prev) => (prev + 1) % images.length);
    setPaused(true);
  };

  return (
    <div className="relative w-full flex flex-col items-center">
      <div
        className="relative w-full flex flex-col items-center"
        onMouseEnter={() => setPaused(true)}
        onMouseLeave={() => setPaused(false)}
      >
        <img
          src={images[current].src}
          alt={images[current].alt}
          className="rounded shadow-lg w-full h-auto object-contain"
        />
        <figcaption className="absolute bottom-0 left-0 right-0 text-sm text-center bg-black bg-opacity-75 text-white p-2">
          {images[current].caption}
        </figcaption>
      </div>
      {/* Controles */}
      {images.length > 1 && (
        <div className="flex items-center gap-4 mt-2">
          <button
            aria-label="Anterior"
            onClick={prev}
            className="p-2 rounded-full bg-congress-blue hover:bg-congress-blue-dark text-white"
          >
            &#8592;
          </button>
          <div className="flex gap-1">
            {images.map((_, idx) => (
              <button
                key={idx}
                className={`w-2 h-2 rounded-full ${idx === current ? "bg-congress-cyan" : "bg-gray-300"}`}
                onClick={() => goTo(idx)}
                aria-label={`Ir a la imagen ${idx + 1}`}
              />
            ))}
          </div>
          <button
            aria-label="Siguiente"
            onClick={next}
            className="p-2 rounded-full bg-congress-blue hover:bg-congress-blue-dark text-white"
          >
            &#8594;
          </button>
        </div>
      )}
    </div>
  );
};

export default ImageSlider;