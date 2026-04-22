import { useScroll, useTransform, useSpring, MotionValue } from "framer-motion";

/**
 * Skill: Premium Scroll Animations
 * Proporciona valores de animación optimizados para efectos de scroll suaves y modernos.
 */
export const usePremiumScroll = () => {
  const { scrollYProgress } = useScroll();
  
  const scale = useSpring(useTransform(scrollYProgress, [0, 0.2], [1, 0.95]), {
    stiffness: 100,
    damping: 30,
    restDelta: 0.001
  });

  const opacity = useTransform(scrollYProgress, [0, 0.2], [1, 0]);
  const blur = useTransform(scrollYProgress, [0, 0.1], ["blur(0px)", "blur(10px)"]);

  return { scale, opacity, blur, scrollYProgress };
};

/**
 * Skill: Staggered Entrance
 * Genera variantes para animaciones de entrada escalonadas de alto impacto.
 */
export const staggeredContainer = (staggerChildren = 0.1, delayChildren = 0) => ({
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren,
      delayChildren,
    },
  },
});

export const entranceItem = {
  hidden: { y: 20, opacity: 0 },
  show: { 
    y: 0, 
    opacity: 1,
    transition: {
      type: "spring",
      stiffness: 260,
      damping: 20,
    }
  },
};
