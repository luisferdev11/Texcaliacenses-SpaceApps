import React, { useState, useEffect, useRef } from "react";

const ResponsiveSection = ({ children }) => {
  const [flexDirection, setFlexDirection] = useState("flex-col");
  const sectionRef = useRef(null);

  useEffect(() => {
    const handleResize = (entries) => {
      for (let entry of entries) {
        const width = entry.contentRect.width;
        if (width >= 350) {
          setFlexDirection("flex-row");
        } else {
          setFlexDirection("flex-col");
        }
      }
    };

    const resizeObserver = new ResizeObserver(handleResize);
    if (sectionRef.current) {
      resizeObserver.observe(sectionRef.current);
    }

    return () => {
      if (sectionRef.current) {
        resizeObserver.unobserve(sectionRef.current);
      }
    };
  }, []);

  return (
    <section
      ref={sectionRef}
      className={`flex ${flexDirection} text-sm gap-y-2`}
    >
      {children}
    </section>
  );
};

export default ResponsiveSection;
