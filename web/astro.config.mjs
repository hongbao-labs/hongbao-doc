import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

const receiverSidebar = [
  {
    label: 'Receiver',
    translations: { 'zh-CN': '持卡人' },
    items: [
      { slug: 'receiver/overview' },
      { slug: 'receiver/guide' },
      { slug: 'receiver/faq' },
    ],
  },
];

const issuerSidebar = [
  {
    label: 'Issuer',
    translations: { 'zh-CN': '发卡方' },
    items: [
      { slug: 'issuer/overview' },
      { slug: 'issuer/guide' },
      { slug: 'issuer/customization' },
      { slug: 'issuer/faq' },
    ],
  },
];

export default defineConfig({
  devToolbar: { enabled: false },
  site: 'https://docs.hongbao.digital',
  integrations: [
    starlight({
      title: 'Hongbao',
      description: 'On-chain asset distribution protocol documentation',
      logo: {
        src: './src/assets/hongbao-logo.svg',
        alt: 'Hongbao',
      },
      defaultLocale: 'en',
      locales: {
        en: {
          label: 'English',
          lang: 'en',
        },
        zh: {
          label: '中文',
          lang: 'zh-CN',
        },
      },
      social: [
        {
          icon: 'github',
          label: 'GitHub',
          href: 'https://github.com/hongbao-labs/hongbao-doc',
        },
      ],
      customCss: ['./src/styles/custom.css'],
      sidebar: [
        {
          label: 'Overview',
          translations: { 'zh-CN': '总览' },
          items: [
            {
              label: 'Overview',
              link: '/',
              translations: { 'zh-CN': '总览' },
            },
            { slug: 'contact' },
          ],
        },
        ...receiverSidebar,
        ...issuerSidebar,
      ],
      head: [
        {
          tag: 'meta',
          attrs: {
            name: 'theme-color',
            content: '#D42020',
          },
        },
      ],
    }),
  ],
});
