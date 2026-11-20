import { Component } from 'react'

export default class ErrorBoundary extends Component {
  state = { hasError: false, error: null }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, info) {
    console.error('[ErrorBoundary]', error, info)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          display: 'flex', flexDirection: 'column',
          alignItems: 'center', justifyContent: 'center',
          height: 240, gap: 12, color: '#94A3B8',
        }}>
          <span style={{ fontSize: 32 }}>⚠️</span>
          <p style={{ fontSize: 14 }}>Something went wrong loading this section.</p>
          <p style={{ fontSize: 12, color: '#475569', maxWidth: 320, textAlign: 'center' }}>
            {this.state.error?.message || 'Unknown error'}
          </p>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
            style={{
              fontSize: 12, padding: '6px 14px', borderRadius: 6,
              border: '1px solid #1E2329', background: 'transparent',
              color: '#94A3B8', cursor: 'pointer',
            }}
          >
            Try again
          </button>
        </div>
      )
    }
    return this.props.children
  }
}
