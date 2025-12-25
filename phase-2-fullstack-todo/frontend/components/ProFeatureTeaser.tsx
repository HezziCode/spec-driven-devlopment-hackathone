'use client';

// Pro feature teaser component with blurred content and upgrade button for TaskWave Dashboard
// Displays premium features with "Coming Soon" badge and upgrade modal trigger

import React from 'react';
import WaveButton from './WaveButton';

interface ProFeatureTeaserProps {
  onUpgradeClick?: () => void;
}

const ProFeatureTeaser: React.FC<ProFeatureTeaserProps> = ({ onUpgradeClick }) => {
  const features = [
    { title: 'AI Magic Tags', description: 'Auto-generate relevant tags for your tasks' },
    { title: 'Smart Priorities', description: 'AI-powered priority suggestions based on deadlines and context' },
    { title: 'Sub-task Breakdowns', description: 'Automatically break complex tasks into manageable sub-tasks' },
    { title: 'Advanced Analytics', description: 'Detailed insights into your productivity patterns' },
    { title: 'Custom Themes', description: 'Personalize your dashboard with premium themes' },
    { title: 'Priority Support', description: 'Get faster responses to your support requests' },
  ];

  return (
    <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      {/* Coming Soon badge */}
      <div className="relative">
        <div className="absolute -top-3 left-1/2 transform -translate-x-1/2 z-10">
          <span className="px-4 py-1.5 rounded-full text-sm font-bold bg-gradient-to-r from-amber-400 to-orange-500 text-white shadow-lg">
            Coming Soon
          </span>
        </div>
      </div>

      <div className="pt-8 p-6">
        <h2 className="text-2xl font-bold text-center text-gray-900 dark:text-white mb-2">
          Unlock Premium Productivity
        </h2>
        <p className="text-center text-gray-600 dark:text-gray-400 mb-8">
          Upgrade to Pro for ultimate productivity waves!
        </p>

        {/* Blurred content area */}
        <div className="relative rounded-xl bg-white dark:bg-slate-700 p-6 mb-8 backdrop-blur-sm">
          {/* Blur effect overlay */}
          <div className="absolute inset-0 bg-white dark:bg-slate-800 backdrop-blur-[2px] rounded-xl z-0"></div>

          <div className="relative z-10">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 text-center">
              Premium Features
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {features.map((feature, index) => (
                <div
                  key={index}
                  className="bg-white dark:bg-slate-700 rounded-lg p-4 border border-slate-200/50 dark:border-slate-600/50"
                >
                  <h4 className="font-medium text-gray-900 dark:text-white mb-1">{feature.title}</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">{feature.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Upgrade button */}
        <div className="text-center">
          <WaveButton
            variant="primary"
            size="lg"
            className="px-8 py-3 text-lg font-bold relative overflow-hidden group"
            onClick={onUpgradeClick}
          >
            <span className="relative z-10">Go Pro</span>
            {/* Cyan glow effect on hover */}
            <div className="absolute inset-0 bg-gradient-to-r from-teal-500 to-cyan-500 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-md -z-10"></div>
          </WaveButton>

          <p className="mt-3 text-sm text-gray-600 dark:text-gray-400">
            Unlock these premium features and more
          </p>
        </div>
      </div>

      {/* Decorative wave elements */}
      <div className="absolute bottom-0 left-0 right-0 h-12 overflow-hidden">
        <svg
          className="absolute bottom-0 w-full h-12 text-slate-200 dark:text-slate-800"
          viewBox="0 0 1200 120"
          preserveAspectRatio="none"
        >
          <path
            d="M0,0V46.29c47.79,22.2,103.59,32.17,158,28,70.36-5.37,136.33-33.31,206.8-37.5C438.64,32.43,512.34,53.67,583,72.05c69.27,18,138.3,24.88,209.4,13.08,36.15-6,69.85-17.84,104.45-29.34C989.49,25,1113-14.29,1200,52.47V0Z"
            opacity=".2"
            className="fill-current"
          ></path>
          <path
            d="M0,0V15.81C13,36.92,27.64,56.86,47.69,72.05,99.41,111.27,165,111,224.58,91.58c31.15-10.15,60.09-26.07,89.67-39.8,40.92-19,84.73-46,130.83-49.67,36.26-2.85,70.9,9.42,98.6,31.56,31.77,25.39,62.32,62,103.63,73,40.44,10.79,81.35-6.69,119.13-24.28s75.16-39,116.92-43.05c59.73-5.85,113.28,22.88,168.9,38.84,30.2,8.66,59,6.17,87.09-7.5,22.43-10.89,48-26.93,60.65-49.24V0Z"
            opacity=".5"
            className="fill-current"
          ></path>
          <path
            d="M0,0V5.63C149.93,59,314.09,71.32,475.83,42.57c43-7.64,84.23-20.12,127.61-26.46,59-8.63,112.48,12.24,165.56,35.4C827.93,77.22,886,95.24,951.2,90c86.53-7,172.46-45.71,248.8-84.81V0Z"
            className="fill-current"
          ></path>
        </svg>
      </div>
    </div>
  );
};

export default ProFeatureTeaser;