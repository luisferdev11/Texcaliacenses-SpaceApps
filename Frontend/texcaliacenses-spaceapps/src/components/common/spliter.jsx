import React, { useState, useEffect, useRef } from "react";
import "./spliter.css";

const HorizontalSpliter = ({ children, initialSize = 50 }) => {
  const childrenArray = React.Children.toArray(children);
  const firstChild = childrenArray[0];
  const secondChild = childrenArray[1];

  const [size, setSize] = useState(initialSize);
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef(null);
  const [isSmallScreen, setIsSmallScreen] = useState(false);

  useEffect(() => {
    setSize(initialSize);
  }, [initialSize]);

  useEffect(() => {
    const handleResize = () => {
      setIsSmallScreen(window.innerWidth <= 990);
    };

    handleResize(); // Call once to set initial state
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (isDragging && containerRef.current) {
        const containerRect = containerRef.current.getBoundingClientRect();
        const containerWidth = containerRect.width;
        const mouseX = e.clientX - containerRect.left;
        const minSize = 20; // 20% of container width
        const maxSize = 80; // 80% of container width
        const newSize = (mouseX / containerWidth) * 100;
        setSize(Math.max(minSize, Math.min(maxSize, newSize)));
      }
    };

    const handleMouseUp = () => {
      setIsDragging(false);
      document.body.classList.remove("no-select");
    };

    if (isDragging) {
      document.addEventListener("mousemove", handleMouseMove);
      document.addEventListener("mouseup", handleMouseUp);
    }

    return () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
    };
  }, [isDragging]);

  const handleMouseDown = (e) => {
    e.preventDefault();
    setIsDragging(true);
    document.body.classList.add("no-select");
  };

  return (
    <div className="rounded-lg h-full base:gap-1 w-full">
      <div ref={containerRef} className="w-full h-full flex flex-row">
        <div
          className={`h-full`}
          style={!isSmallScreen ? { width: `${size}%` } : {}}
        >
          {firstChild}
        </div>
        <div
          onMouseDown={handleMouseDown}
          className="hidden md:block cursor-ew-resize h-full pb-4 rounded-full"
        >
          <div className="flex flex-col justify-center h-full hover:bg-neutral-200 rounded-full">
            <div
              className={`${
                size === 0 ? "hidden" : "block"
              } h-16 w-1 bg-black rounded-full overflow-y-auto`}
            ></div>
          </div>
        </div>
        <div className="h-full flex-1">{secondChild}</div>
      </div>
    </div>
  );
};

export default HorizontalSpliter;
