import { Swiper, SwiperSlide, useSwiper } from 'swiper/react';
import { Pagination } from 'swiper/modules';

// 1. Create a component for the buttons
const SwiperNavButtons = () => {
  const swiper = useSwiper();

  return (
    <div className="swiper-nav-btns">
      <button onClick={() => swiper.slidePrev()}>Prev</button>
      <button onClick={() => swiper.slideNext()}>Next</button>
    </div>
  );
};

export default function App() {
  return (
    <Swiper
      modules={[Pagination]} // Notice Navigation module isn't strictly needed here
      spaceBetween={45}
      slidesPerView={5}
      pagination={{ clickable: true }}
    >
      {/* 2. Place the buttons inside the Swiper component */}
      <SwiperNavButtons />

      <SwiperSlide>Slide 1</SwiperSlide>
      <SwiperSlide>Slide 2</SwiperSlide>
      <SwiperSlide>Slide 3</SwiperSlide>
    </Swiper>
  );
}