import React from 'react';
import type { Meta, StoryObj } from '@storybook/react';
import { Badge } from '../components/ui/Badge';
import { CheckIcon, AlertIcon } from '../assets/icons';

const meta: Meta<typeof Badge> = {
  title: 'Components/Badge',
  component: Badge,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'primary', 'success', 'warning', 'error', 'info', 'critical', 'high', 'medium', 'low'],
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg'],
    },
    dot: {
      control: 'boolean',
    },
  },
};

export default meta;
type Story = StoryObj<typeof Badge>;

export const Default: Story = {
  args: {
    children: 'Default',
  },
};

export const Primary: Story = {
  args: {
    variant: 'primary',
    children: 'Primary',
  },
};

export const Success: Story = {
  args: {
    variant: 'success',
    children: 'Success',
  },
};

export const Warning: Story = {
  args: {
    variant: 'warning',
    children: 'Warning',
  },
};

export const Error: Story = {
  args: {
    variant: 'error',
    children: 'Error',
  },
};

export const WithDot: Story = {
  args: {
    variant: 'success',
    children: 'Active',
    dot: true,
  },
};

export const WithIcon: Story = {
  args: {
    variant: 'success',
    children: 'Verified',
    leftIcon: <CheckIcon size={12} />,
  },
};

export const RiskLevels: Story = {
  render: () => (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
      <Badge variant="critical">Critical</Badge>
      <Badge variant="high">High</Badge>
      <Badge variant="medium">Medium</Badge>
      <Badge variant="low">Low</Badge>
    </div>
  ),
};

export const ComplianceStatuses: Story = {
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', alignItems: 'flex-start' }}>
      <Badge variant="success" leftIcon={<CheckIcon size={12} />}>GDPR Compliant</Badge>
      <Badge variant="warning" leftIcon={<AlertIcon size={12} />}>FCA Review Required</Badge>
      <Badge variant="error" leftIcon={<AlertIcon size={12} />}>Tax Non-Compliant</Badge>
      <Badge variant="info">Employment Verified</Badge>
    </div>
  ),
};

export const Sizes: Story = {
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', alignItems: 'flex-start' }}>
      <Badge size="sm" variant="primary">Small</Badge>
      <Badge size="md" variant="primary">Medium</Badge>
      <Badge size="lg" variant="primary">Large</Badge>
    </div>
  ),
};

export const AllVariants: Story = {
  render: () => (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
      <Badge variant="default">Default</Badge>
      <Badge variant="primary">Primary</Badge>
      <Badge variant="success">Success</Badge>
      <Badge variant="warning">Warning</Badge>
      <Badge variant="error">Error</Badge>
      <Badge variant="info">Info</Badge>
      <Badge variant="critical">Critical</Badge>
      <Badge variant="high">High</Badge>
      <Badge variant="medium">Medium</Badge>
      <Badge variant="low">Low</Badge>
    </div>
  ),
};
