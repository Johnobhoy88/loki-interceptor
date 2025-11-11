import React from 'react';
import type { Meta, StoryObj } from '@storybook/react';
import { Input } from '../components/ui/Input';
import { SearchIcon, AlertIcon } from '../assets/icons';

const meta: Meta<typeof Input> = {
  title: 'Components/Input',
  component: Input,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg'],
    },
    status: {
      control: 'select',
      options: ['default', 'error', 'success', 'warning'],
    },
    disabled: {
      control: 'boolean',
    },
    fullWidth: {
      control: 'boolean',
    },
  },
};

export default meta;
type Story = StoryObj<typeof Input>;

export const Default: Story = {
  args: {
    placeholder: 'Enter text...',
  },
};

export const WithLabel: Story = {
  args: {
    label: 'Email Address',
    placeholder: 'you@example.com',
    type: 'email',
  },
};

export const WithHelperText: Story = {
  args: {
    label: 'Username',
    placeholder: 'Enter your username',
    helperText: 'Must be at least 3 characters long',
  },
};

export const WithError: Story = {
  args: {
    label: 'Password',
    placeholder: 'Enter password',
    type: 'password',
    error: 'Password must be at least 8 characters',
  },
};

export const Success: Story = {
  args: {
    label: 'Email',
    placeholder: 'you@example.com',
    value: 'user@example.com',
    status: 'success',
    helperText: 'Email is available',
  },
};

export const WithLeftIcon: Story = {
  args: {
    placeholder: 'Search...',
    leftIcon: <SearchIcon size={18} />,
  },
};

export const WithRightIcon: Story = {
  args: {
    placeholder: 'Enter value',
    status: 'error',
    rightIcon: <AlertIcon size={18} />,
  },
};

export const Disabled: Story = {
  args: {
    label: 'Disabled Input',
    placeholder: 'Cannot edit',
    value: 'Read only value',
    disabled: true,
  },
};

export const Sizes: Story = {
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', width: '300px' }}>
      <Input size="sm" placeholder="Small input" />
      <Input size="md" placeholder="Medium input" />
      <Input size="lg" placeholder="Large input" />
    </div>
  ),
};

export const AllStates: Story = {
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', width: '300px' }}>
      <Input label="Default" placeholder="Default state" />
      <Input label="Error" placeholder="Error state" status="error" error="This field has an error" />
      <Input label="Success" placeholder="Success state" status="success" helperText="Looks good!" />
      <Input label="Warning" placeholder="Warning state" status="warning" helperText="Please verify this" />
      <Input label="Disabled" placeholder="Disabled state" disabled />
    </div>
  ),
};
