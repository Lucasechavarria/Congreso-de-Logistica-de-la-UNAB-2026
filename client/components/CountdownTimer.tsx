import { useState, useEffect } from "react";
import { motion } from "framer-motion";

interface TimeLeft {
    days: number;
    hours: number;
    minutes: number;
    seconds: number;
}

export default function CountdownTimer() {
    const targetDate = new Date("2026-11-07T09:00:00").getTime();

    const calculateTimeLeft = (): TimeLeft => {
        const now = new Date().getTime();
        const difference = targetDate - now;

        let timeLeft: TimeLeft = {
            days: 0,
            hours: 0,
            minutes: 0,
            seconds: 0
        };

        if (difference > 0) {
            timeLeft = {
                days: Math.floor(difference / (1000 * 60 * 60 * 24)),
                hours: Math.floor((difference / (1000 * 60 * 60)) % 24),
                minutes: Math.floor((difference / 1000 / 60) % 60),
                seconds: Math.floor((difference / 1000) % 60),
            };
        }

        return timeLeft;
    };

    const [timeLeft, setTimeLeft] = useState<TimeLeft>(calculateTimeLeft());

    useEffect(() => {
        const timer = setInterval(() => {
            setTimeLeft(calculateTimeLeft());
        }, 1000);

        return () => clearInterval(timer);
    }, []);

    const TimeUnit = ({ value, label }: { value: number; label: string }) => (
        <div className="flex flex-col items-center mx-2 md:mx-4">
            <motion.div
                key={value}
                initial={{ y: 10, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                className="text-3xl md:text-5xl font-black text-congress-cyan tabular-nums drop-shadow-[0_0_10px_rgba(167,139,250,0.5)]"
            >
                {value.toString().padStart(2, '0')}
            </motion.div>
            <div className="text-[10px] md:text-xs uppercase tracking-widest text-white/60 font-bold mt-1">
                {label}
            </div>
        </div>
    );

    return (
        <div className="flex items-center justify-center p-6 bg-white/5 backdrop-blur-md rounded-2xl border border-white/10 shadow-2xl mt-8">
            <TimeUnit value={timeLeft.days} label="Días" />
            <div className="text-2xl md:text-4xl font-light text-white/20 mb-4">:</div>
            <TimeUnit value={timeLeft.hours} label="Horas" />
            <div className="text-2xl md:text-4xl font-light text-white/20 mb-4">:</div>
            <TimeUnit value={timeLeft.minutes} label="Mins" />
            <div className="text-2xl md:text-4xl font-light text-white/20 mb-4">:</div>
            <TimeUnit value={timeLeft.seconds} label="Segs" />
        </div>
    );
}
