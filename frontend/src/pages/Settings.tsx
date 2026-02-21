import { useEffect, useState } from 'react';
import { settingsApi } from '../services/api';
import type { Account, RiskConfig, NotificationConfig, AppConfig } from '../types';

export default function Settings() {
  const [_account, setAccount] = useState<Account | null>(null);
  const [_riskConfig, setRiskConfig] = useState<RiskConfig | null>(null);
  const [_notificationConfig, setNotificationConfig] = useState<NotificationConfig | null>(null);
  const [_appConfig, setAppConfig] = useState<AppConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState<'account' | 'risk' | 'notify' | 'app'>('account');

  const [accountForm, setAccountForm] = useState({
    total_assets: 100000,
    available_cash: 50000,
  });

  const [riskForm, setRiskForm] = useState({
    max_position_ratio: 20,
    max_positions: 5,
    daily_loss_limit: 5,
    weekly_loss_limit: 10,
    monthly_loss_limit: 20,
    default_stop_loss: -5,
    default_take_profit: 10,
    trailing_stop: false,
    trailing_stop_percent: 3,
    position_size_by_win_rate: true,
    min_win_rate: 45,
    allow_add_position: false,
    max_add_position: 1,
    force_close_on_risk: true,
    cooling_period_minutes: 30,
  });

  const [notificationForm, setNotificationForm] = useState({
    signal_notify: true,
    trade_notify: true,
    stop_loss_notify: true,
  });

  const [appForm, setAppForm] = useState({
    theme: 'light',
  });

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const res = await settingsApi.getAll();
      const data = res.data;
      setAccount(data.account);
      setRiskConfig(data.risk_config);
      setNotificationConfig(data.notification_config);
      setAppConfig(data.app_config);

      setAccountForm({
        total_assets: data.account.total_assets,
        available_cash: data.account.available_cash,
      });
      setRiskForm({
        max_position_ratio: data.risk_config.max_position_ratio || 20,
        max_positions: data.risk_config.max_positions || 5,
        daily_loss_limit: data.risk_config.daily_loss_limit || 5,
        weekly_loss_limit: data.risk_config.weekly_loss_limit || 10,
        monthly_loss_limit: data.risk_config.monthly_loss_limit || 20,
        default_stop_loss: data.risk_config.default_stop_loss || -5,
        default_take_profit: data.risk_config.default_take_profit || 10,
        trailing_stop: data.risk_config.trailing_stop || false,
        trailing_stop_percent: data.risk_config.trailing_stop_percent || 3,
        position_size_by_win_rate: data.risk_config.position_size_by_win_rate ?? true,
        min_win_rate: data.risk_config.min_win_rate || 45,
        allow_add_position: data.risk_config.allow_add_position ?? false,
        max_add_position: data.risk_config.max_add_position || 1,
        force_close_on_risk: data.risk_config.force_close_on_risk ?? true,
        cooling_period_minutes: data.risk_config.cooling_period_minutes || 30,
      });
      setNotificationForm({
        signal_notify: data.notification_config.signal_notify,
        trade_notify: data.notification_config.trade_notify,
        stop_loss_notify: data.notification_config.stop_loss_notify,
      });
      setAppForm({
        theme: data.app_config.theme,
      });
    } catch (error) {
      console.error('Failed to load settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveAccount = async () => {
    setSaving(true);
    try {
      await settingsApi.updateAccount(accountForm);
      alert('保存成功');
    } catch (error) {
      console.error('Failed to save account:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleSaveRisk = async () => {
    setSaving(true);
    try {
      await settingsApi.updateRiskConfig(riskForm);
      alert('保存成功');
    } catch (error) {
      console.error('Failed to save risk config:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleSaveNotification = async () => {
    setSaving(true);
    try {
      await settingsApi.updateNotificationConfig(notificationForm);
      alert('保存成功');
    } catch (error) {
      console.error('Failed to save notification config:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleSaveApp = async () => {
    setSaving(true);
    try {
      await settingsApi.updateAppConfig(appForm);
      alert('保存成功');
    } catch (error) {
      console.error('Failed to save app config:', error);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1>设置</h1>
      </div>

      <div className="review-tabs" style={{ maxWidth: '800px' }}>
        <button className={`review-tab ${activeTab === 'account' ? 'active' : ''}`} onClick={() => setActiveTab('account')}>
          <span className="tab-icon">💰</span><span>账户</span>
        </button>
        <button className={`review-tab ${activeTab === 'risk' ? 'active' : ''}`} onClick={() => setActiveTab('risk')}>
          <span className="tab-icon">🛡️</span><span>风控</span>
        </button>
        <button className={`review-tab ${activeTab === 'notify' ? 'active' : ''}`} onClick={() => setActiveTab('notify')}>
          <span className="tab-icon">🔔</span><span>通知</span>
        </button>
        <button className={`review-tab ${activeTab === 'app' ? 'active' : ''}`} onClick={() => setActiveTab('app')}>
          <span className="tab-icon">⚙️</span><span>应用</span>
        </button>
      </div>

      {activeTab === 'account' && (
        <div className="review-section" style={{ maxWidth: '600px' }}>
          <div className="card">
            <h3 style={{ marginBottom: '20px' }}>账户资产</h3>
            <div className="form-row">
              <div className="form-group">
                <label>总资产</label>
                <div className="input-wrapper">
                  <input type="number" value={accountForm.total_assets} onChange={(e) => setAccountForm({ ...accountForm, total_assets: parseFloat(e.target.value) })} placeholder="100000" />
                  <span className="input-suffix">元</span>
                </div>
              </div>
              <div className="form-group">
                <label>可用资金</label>
                <div className="input-wrapper">
                  <input type="number" value={accountForm.available_cash} onChange={(e) => setAccountForm({ ...accountForm, available_cash: parseFloat(e.target.value) })} placeholder="50000" />
                  <span className="input-suffix">元</span>
                </div>
              </div>
            </div>
            <button className="btn btn-primary" onClick={handleSaveAccount} disabled={saving}>{saving ? '保存中...' : '保存设置'}</button>
          </div>
        </div>
      )}

      {activeTab === 'risk' && (
        <div className="review-section" style={{ maxWidth: '700px' }}>
          <div className="card">
            <h3 style={{ marginBottom: '20px' }}>仓位控制</h3>
            <div className="form-row">
              <div className="form-group">
                <label>单票最大仓位</label>
                <div className="input-wrapper">
                  <input type="number" value={riskForm.max_position_ratio} onChange={(e) => setRiskForm({ ...riskForm, max_position_ratio: parseFloat(e.target.value) })} placeholder="20" />
                  <span className="input-suffix">%</span>
                </div>
              </div>
              <div className="form-group">
                <label>最大持仓数</label>
                <input type="number" value={riskForm.max_positions} onChange={(e) => setRiskForm({ ...riskForm, max_positions: parseInt(e.target.value) })} placeholder="5" />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>是否按胜率调仓</label>
                <div className={`toggle-switch ${riskForm.position_size_by_win_rate ? 'active' : ''}`} onClick={() => setRiskForm({ ...riskForm, position_size_by_win_rate: !riskForm.position_size_by_win_rate })} />
              </div>
              <div className="form-group">
                <label>最低胜率要求</label>
                <div className="input-wrapper">
                  <input type="number" value={riskForm.min_win_rate} onChange={(e) => setRiskForm({ ...riskForm, min_win_rate: parseFloat(e.target.value) })} placeholder="45" />
                  <span className="input-suffix">%</span>
                </div>
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>允许补仓</label>
                <div className={`toggle-switch ${riskForm.allow_add_position ? 'active' : ''}`} onClick={() => setRiskForm({ ...riskForm, allow_add_position: !riskForm.allow_add_position })} />
              </div>
              <div className="form-group">
                <label>最大补仓次数</label>
                <input type="number" value={riskForm.max_add_position} onChange={(e) => setRiskForm({ ...riskForm, max_add_position: parseInt(e.target.value) })} placeholder="1" />
              </div>
            </div>

            <h3 style={{ marginTop: '30px', marginBottom: '20px' }}>亏损限制</h3>
            <div className="form-row">
              <div className="form-group">
                <label>日内亏损限制</label>
                <div className="input-wrapper">
                  <input type="number" step="0.1" value={riskForm.daily_loss_limit} onChange={(e) => setRiskForm({ ...riskForm, daily_loss_limit: parseFloat(e.target.value) })} placeholder="5" />
                  <span className="input-suffix">%</span>
                </div>
              </div>
              <div className="form-group">
                <label>周亏损限制</label>
                <div className="input-wrapper">
                  <input type="number" step="0.1" value={riskForm.weekly_loss_limit} onChange={(e) => setRiskForm({ ...riskForm, weekly_loss_limit: parseFloat(e.target.value) })} placeholder="10" />
                  <span className="input-suffix">%</span>
                </div>
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>月亏损限制</label>
                <div className="input-wrapper">
                  <input type="number" step="0.1" value={riskForm.monthly_loss_limit} onChange={(e) => setRiskForm({ ...riskForm, monthly_loss_limit: parseFloat(e.target.value) })} placeholder="20" />
                  <span className="input-suffix">%</span>
                </div>
              </div>
              <div className="form-group">
                <label>触发风控强平</label>
                <div className={`toggle-switch ${riskForm.force_close_on_risk ? 'active' : ''}`} onClick={() => setRiskForm({ ...riskForm, force_close_on_risk: !riskForm.force_close_on_risk })} />
              </div>
            </div>

            <h3 style={{ marginTop: '30px', marginBottom: '20px' }}>止盈止损</h3>
            <div className="form-row">
              <div className="form-group">
                <label>默认止损</label>
                <div className="input-wrapper">
                  <input type="number" step="0.1" value={riskForm.default_stop_loss} onChange={(e) => setRiskForm({ ...riskForm, default_stop_loss: parseFloat(e.target.value) })} placeholder="-5" />
                  <span className="input-suffix">%</span>
                </div>
              </div>
              <div className="form-group">
                <label>默认止盈</label>
                <div className="input-wrapper">
                  <input type="number" step="0.1" value={riskForm.default_take_profit} onChange={(e) => setRiskForm({ ...riskForm, default_take_profit: parseFloat(e.target.value) })} placeholder="10" />
                  <span className="input-suffix">%</span>
                </div>
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>启用移动止损</label>
                <div className={`toggle-switch ${riskForm.trailing_stop ? 'active' : ''}`} onClick={() => setRiskForm({ ...riskForm, trailing_stop: !riskForm.trailing_stop })} />
              </div>
              <div className="form-group">
                <label>移动止损幅度</label>
                <div className="input-wrapper">
                  <input type="number" step="0.1" value={riskForm.trailing_stop_percent} onChange={(e) => setRiskForm({ ...riskForm, trailing_stop_percent: parseFloat(e.target.value) })} placeholder="3" />
                  <span className="input-suffix">%</span>
                </div>
              </div>
            </div>

            <h3 style={{ marginTop: '30px', marginBottom: '20px' }}>交易限制</h3>
            <div className="form-group">
              <label>亏损后冷却时间</label>
              <div className="input-wrapper" style={{ maxWidth: '200px' }}>
                <input type="number" value={riskForm.cooling_period_minutes} onChange={(e) => setRiskForm({ ...riskForm, cooling_period_minutes: parseInt(e.target.value) })} placeholder="30" />
                <span className="input-suffix">分钟</span>
              </div>
            </div>

            <button className="btn btn-primary" onClick={handleSaveRisk} disabled={saving} style={{ marginTop: '20px' }}>{saving ? '保存中...' : '保存设置'}</button>
          </div>
        </div>
      )}

      {activeTab === 'notify' && (
        <div className="review-section" style={{ maxWidth: '600px' }}>
          <div className="card">
            <h3 style={{ marginBottom: '20px' }}>通知提醒</h3>
            <div className="notify-list">
              <div className="notify-item">
                <div className="notify-info"><span className="notify-title">信号提醒</span><span className="notify-desc">持仓触发止盈止损时提醒</span></div>
                <div className={`toggle-switch ${notificationForm.signal_notify ? 'active' : ''}`} onClick={() => setNotificationForm({ ...notificationForm, signal_notify: !notificationForm.signal_notify })} />
              </div>
              <div className="notify-item">
                <div className="notify-info"><span className="notify-title">交易提醒</span><span className="notify-desc">开仓平仓操作提醒</span></div>
                <div className={`toggle-switch ${notificationForm.trade_notify ? 'active' : ''}`} onClick={() => setNotificationForm({ ...notificationForm, trade_notify: !notificationForm.trade_notify })} />
              </div>
              <div className="notify-item">
                <div className="notify-info"><span className="notify-title">止损提醒</span><span className="notify-desc">接近止损价时提醒</span></div>
                <div className={`toggle-switch ${notificationForm.stop_loss_notify ? 'active' : ''}`} onClick={() => setNotificationForm({ ...notificationForm, stop_loss_notify: !notificationForm.stop_loss_notify })} />
              </div>
            </div>
            <button className="btn btn-primary" onClick={handleSaveNotification} disabled={saving} style={{ marginTop: '20px' }}>{saving ? '保存中...' : '保存设置'}</button>
          </div>
        </div>
      )}

      {activeTab === 'app' && (
        <div className="review-section" style={{ maxWidth: '600px' }}>
          <div className="card">
            <h3 style={{ marginBottom: '20px' }}>应用偏好</h3>
            <div className="form-group">
              <label>主题风格</label>
              <select value={appForm.theme} onChange={(e) => setAppForm({ ...appForm, theme: e.target.value })}>
                <option value="light">浅色模式</option>
                <option value="dark">深色模式</option>
              </select>
            </div>
            <button className="btn btn-primary" onClick={handleSaveApp} disabled={saving}>{saving ? '保存中...' : '保存设置'}</button>
          </div>
        </div>
      )}
    </div>
  );
}
