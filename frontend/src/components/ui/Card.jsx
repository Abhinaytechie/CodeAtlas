import { cn } from '../../lib/utils';
import { motion } from 'framer-motion';

const Card = ({ className, children, glass = false, ...props }) => {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className={cn(
                'rounded-2xl border border-border bg-surface p-6 shadow-sm',
                glass && 'glass-card',
                className
            )}
            {...props}
        >
            {children}
        </motion.div>
    );
};

export { Card };
