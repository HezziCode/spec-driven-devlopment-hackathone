'use client';

import React, { useState } from 'react';
import { ListTodo, Calendar, Clock, User, ArrowRight, MessageCircle, Share2 } from 'lucide-react';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import NeuralBackground from '@/components/NeuralBackground';

// Custom styles for theme and typography
const GlobalStyles = () => (
  <style>{`
    body {
      transition: background-color 0.3s ease-in-out;
      background-color: #0f172a; /* Dark background */
    }

    /* Gradient text for headlines */
    .gradient-text-teal {
      background-clip: text;
      -webkit-background-clip: text;
      color: transparent;
      background-image: linear-gradient(to right, #2dd4bf, #06b6d4, #0e7490); /* Teal-Cyan blend */
      transition: all 0.3s ease-in-out;
    }
  `}</style>
);

const BlogPage = () => {
  const accentColor = 'text-cyan-400';
  const borderColor = 'border-slate-700/50';
  const textColor = 'text-slate-200';
  const iconColor = 'text-slate-400';
  const hoverBgColor = 'hover:bg-slate-800/50';

  // Mock user data (in a real app, this would come from auth context)
  const mockUser = {
    id: 'demo-user',
    username: 'Demo User',
    email: 'demo@example.com'
  };

  // Mock notifications data
  const mockNotifications: any[] = [];

  // Sample blog posts
  const blogPosts = [
    {
      id: 1,
      title: "The Psychology of Productivity: Why Less is More",
      excerpt: "Discover how minimalist design principles can dramatically improve your focus and task completion rates.",
      author: "Sarah Johnson",
      date: "December 15, 2024",
      readTime: "5 min read",
      tags: ["Productivity", "Psychology", "Design"],
      image: "productivity-psychology"
    },
    {
      id: 2,
      title: "TaskFlow's Journey: From Concept to Launch",
      excerpt: "A behind-the-scenes look at how we built TaskFlow from the ground up with user experience as our guiding principle.",
      author: "Michael Chen",
      date: "December 10, 2024",
      readTime: "7 min read",
      tags: ["Company", "Journey", "Behind the Scenes"],
      image: "company-journey"
    },
    {
      id: 3,
      title: "Mastering Your Flow: 5 Tips for Peak Productivity",
      excerpt: "Practical strategies to help you get into and maintain your most productive state more consistently.",
      author: "David Rodriguez",
      date: "December 5, 2024",
      readTime: "4 min read",
      tags: ["Tips", "Productivity", "Workflow"],
      image: "productivity-tips"
    },
    {
      id: 4,
      title: "Why We Chose a Minimalist Approach to Task Management",
      excerpt: "Exploring the philosophy behind TaskFlow's design decisions and how simplicity leads to better outcomes.",
      author: "Emma Thompson",
      date: "November 28, 2024",
      readTime: "6 min read",
      tags: ["Philosophy", "Design", "Minimalism"],
      image: "minimalism-approach"
    }
  ];

  return (
    <div className="min-h-screen bg-slate-900/40 transition-colors duration-300 relative">
      <GlobalStyles />

      {/* Neural Background - positioned just behind content but above base background */}
      <NeuralBackground />

      <div className="relative z-10">
        <Navbar
          userId={mockUser.id}
          handleAuthAction={() => {}}
          setView={() => {}}
          notifications={mockNotifications}
          onMarkAllRead={() => {}}
          onNotificationClick={() => {}}
        />

        <main className="container mx-auto px-4 py-8">
          <div className="max-w-6xl mx-auto">
            {/* Premium Hero Section */}
            <section className="relative w-full flex flex-col items-center justify-center text-center overflow-visible py-16">
              {/* Premium background elements */}
              <div className="absolute top-0 left-0 w-64 h-64 bg-gradient-to-br from-teal-500/5 to-cyan-500/10 rounded-full blur-[120px] -mt-24 -ml-24" />
              <div className="absolute bottom-0 right-0 w-64 h-64 bg-gradient-to-br from-cyan-500/5 to-blue-500/10 rounded-full blur-[120px] -mb-24 -mr-24" />

              <div className="relative z-10 space-y-6 max-w-4xl w-full">
                {/* Status tag */}
                <div className="inline-flex items-center space-x-2.5 px-4 py-2 rounded-full bg-gradient-to-r from-cyan-500/15 to-teal-500/15 border border-cyan-500/30 backdrop-blur-sm shadow-lg shadow-cyan-500/10">
                  <MessageCircle size={14} className="text-cyan-400" />
                  <span className="text-sm font-semibold text-slate-200">Latest Updates</span>
                </div>

                {/* Premium animated heading */}
                <h1 className="text-4xl md:text-6xl lg:text-7xl font-black tracking-tight leading-tight text-white max-w-3xl mx-auto relative">
                  <span className="relative inline-block">
                    TaskFlow Insights<br />
                    Productivity Stories
                    {/* Curved SVG underline */}
                    <svg
                      className="absolute left-0 -bottom-4 w-full h-4 pointer-events-none sm:-bottom-5 sm:h-5"
                      viewBox="0 0 100 10"
                      preserveAspectRatio="none"
                    >
                      <path
                        d="M2,5 Q50,10 98,5"
                        stroke="url(#blog-grad)"
                        strokeWidth="2"
                        fill="none"
                        strokeLinecap="round"
                        opacity="0.8"
                      />
                      <defs>
                        <linearGradient id="blog-grad" x1="0%" y1="0%" x2="100%" y2="0%">
                          <stop offset="0%" stopColor="#5eead4" />
                          <stop offset="100%" stopColor="#67e8f9" />
                        </linearGradient>
                      </defs>
                    </svg>
                  </span>
                </h1>

                {/* Premium animated paragraph */}
                <p className="text-base md:text-lg text-slate-300/90 font-medium max-w-2xl mx-auto leading-relaxed">
                  Discover tips, stories, and insights about productivity, task management, and building better workflows.
                </p>
              </div>
            </section>

            {/* Featured Posts Section */}
            <section className="py-12">
              <h2 className="text-2xl md:text-3xl font-bold text-white mb-8">Featured Articles</h2>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {blogPosts.slice(0, 2).map(post => (
                  <article
                    key={post.id}
                    className={`group bg-slate-800/30 backdrop-blur-sm rounded-2xl overflow-hidden border ${borderColor} transition-all duration-300 hover:shadow-xl hover:shadow-slate-900/30`}
                  >
                    <div className="p-6">
                      <div className="flex flex-wrap gap-2 mb-4">
                        {post.tags.map(tag => (
                          <span
                            key={tag}
                            className="text-xs font-medium px-2.5 py-1 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>

                      <h3 className="text-xl md:text-2xl font-bold text-white mb-3 group-hover:text-cyan-300 transition-colors">
                        {post.title}
                      </h3>

                      <p className="text-slate-400 mb-4">
                        {post.excerpt}
                      </p>

                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="flex items-center space-x-1.5 text-slate-500">
                            <User size={14} className={iconColor} />
                            <span className="text-sm text-slate-400">{post.author}</span>
                          </div>

                          <div className="flex items-center space-x-1.5 text-slate-500">
                            <Calendar size={14} className={iconColor} />
                            <span className="text-sm text-slate-400">{post.date}</span>
                          </div>

                          <div className="flex items-center space-x-1.5 text-slate-500">
                            <Clock size={14} className={iconColor} />
                            <span className="text-sm text-slate-400">{post.readTime}</span>
                          </div>
                        </div>

                        <button className={`flex items-center space-x-1 text-sm font-medium ${accentColor} ${hoverBgColor} px-3 py-1.5 rounded-lg transition-colors`}>
                          <span>Read More</span>
                          <ArrowRight size={14} />
                        </button>
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            </section>

            {/* All Posts Section */}
            <section className="py-8">
              <h2 className="text-2xl md:text-3xl font-bold text-white mb-8">All Articles</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {blogPosts.slice(2).map(post => (
                  <article
                    key={post.id}
                    className={`group bg-slate-800/20 backdrop-blur-sm rounded-xl p-5 border ${borderColor} transition-all duration-300 hover:shadow-lg hover:shadow-slate-900/20`}
                  >
                    <div className="flex flex-wrap gap-2 mb-3">
                      {post.tags.map(tag => (
                        <span
                          key={tag}
                          className="text-[10px] font-medium px-2 py-1 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>

                    <h3 className="text-lg md:text-xl font-semibold text-white mb-2 group-hover:text-cyan-300 transition-colors">
                      {post.title}
                    </h3>

                    <p className="text-slate-400 text-sm mb-4 line-clamp-2">
                      {post.excerpt}
                    </p>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <div className="flex items-center space-x-1 text-slate-500">
                          <User size={12} className={iconColor} />
                          <span className="text-xs text-slate-400">{post.author}</span>
                        </div>

                        <div className="flex items-center space-x-1 text-slate-500">
                          <Calendar size={12} className={iconColor} />
                          <span className="text-xs text-slate-400">{post.date}</span>
                        </div>
                      </div>

                      <button className={`flex items-center space-x-1 text-xs font-medium ${accentColor} ${hoverBgColor} px-2.5 py-1 rounded transition-colors`}>
                        <span>Read</span>
                        <ArrowRight size={12} />
                      </button>
                    </div>
                  </article>
                ))}
              </div>
            </section>

            {/* Newsletter Signup */}
            <section className="py-16">
              <div className="bg-gradient-to-br from-slate-800/40 to-slate-900/40 backdrop-blur-sm rounded-3xl p-8 border border-slate-700/30 text-center max-w-2xl mx-auto">
                <h2 className="text-2xl md:text-3xl font-bold text-white mb-3">Stay Updated</h2>
                <p className="text-slate-400 mb-6">
                  Subscribe to our newsletter and get the latest articles, tips, and updates delivered to your inbox.
                </p>

                <div className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
                  <input
                    type="email"
                    placeholder="Enter your email"
                    className="flex-1 bg-slate-700/40 border border-slate-600/30 rounded-lg px-4 py-3 text-sm text-white focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 outline-none placeholder:text-slate-500"
                  />
                  <button className="px-6 py-3 bg-gradient-to-r from-cyan-600 to-teal-600 hover:from-cyan-500 hover:to-teal-500 text-white font-medium rounded-lg transition-all duration-300 shadow-lg shadow-cyan-500/20 hover:shadow-cyan-400/30 whitespace-nowrap">
                    Subscribe
                  </button>
                </div>
              </div>
            </section>
          </div>
        </main>

        <Footer />
      </div>
    </div>
  );
};

export default BlogPage;