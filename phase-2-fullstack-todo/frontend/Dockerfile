# syntax=docker/dockerfile:1
# check=skip=SecretsUsedInArgOrEnv

# Stage 1: Install dependencies
FROM node:22-alpine AS deps

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci

# Stage 2: Build the application
FROM node:22-alpine AS builder

WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy source code
COPY . .

# Set build-time environment variables
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

# Build arguments for Next.js public environment variables
ARG NEXT_PUBLIC_API_URL=https://api.chat-task.site
ARG NEXT_PUBLIC_GOOGLE_OAUTH_CLIENT_ID=322039376696-qel1r5o6hu0uvl97b28jq9cvvv1hkoqi.apps.googleusercontent.com
ARG BETTER_AUTH_SECRET
ARG BETTER_AUTH_URL=https://api.chat-task.site

# Set environment variables
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_GOOGLE_OAUTH_CLIENT_ID=$NEXT_PUBLIC_GOOGLE_OAUTH_CLIENT_ID
ENV BETTER_AUTH_SECRET=$BETTER_AUTH_SECRET
ENV BETTER_AUTH_URL=$BETTER_AUTH_URL

# Build the Next.js application
RUN npm run build

# Stage 3: Production image
FROM node:22-alpine AS runner

WORKDIR /app

# Set environment variables
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Create non-root user for security
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy built assets from builder
COPY --from=builder /app/public ./public

# Copy standalone build
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

# Run the application
CMD ["node", "server.js"]
