import type {NextConfig} from 'next';

const nextConfig: NextConfig = {
  /* config options here */
  devIndicators: {
    buildActivity: false,
    buildActivityPosition: 'bottom-right',
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  webpack: (config, { isServer }) => {
    if (!isServer) {
      // Excluir módulos específicos de Node.js del bundle del cliente
      config.resolve.fallback = {
        ...config.resolve.fallback,
        'async_hooks': false,
        'fs': false,
        'net': false,
        'tls': false,
        'child_process': false,
        'worker_threads': false,
        'perf_hooks': false,
        'inspector': false,
        'crypto': false,
        'stream': false,
        'util': false,
        'os': false,
        'path': false,
        'events': false,
        'buffer': false,
        'assert': false,
        'url': false,
        'querystring': false,
        'zlib': false,
        'http': false,
        'https': false,
      };

      // Excluir paquetes específicos de OpenTelemetry y Genkit del cliente
      config.externals = config.externals || [];
      config.externals.push({
        '@opentelemetry/context-async-hooks': 'commonjs @opentelemetry/context-async-hooks',
        '@opentelemetry/api': 'commonjs @opentelemetry/api',
        '@opentelemetry/core': 'commonjs @opentelemetry/core',
        '@opentelemetry/resources': 'commonjs @opentelemetry/resources',
        // Limpieza: sin dependencias Genkit/OTel en frontend
      });
    }
    return config;
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'placehold.co',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'images.unsplash.com',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'picsum.photos',
        port: '',
        pathname: '/**',
      },
    ],
  },
};

export default nextConfig;
