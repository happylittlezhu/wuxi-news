const app = getApp()

Page({
  data: {
    activeTab: 'today',
    topTitle: '无锡市重点关注企业商业动态',
    topSub: '编制：市城运中心 · 来源：政府官网 / 企业公告 / 权威媒体等',
    dateLine: '',
    today: [],
    data: [],
    filteredData: [],
    filteredCount: 0,
    searchQuery: '',
    filterOptions: {
      industry: ['全部产业领域'],
      type: ['全部事项分类'],
      city: ['全部城市'],
      name: ['全部企业']
    },
    filterIndex: {
      industry: 0,
      type: 0,
      city: 0,
      name: 0
    },
    filterDisplay: {
      industry: '全部产业领域',
      type: '全部事项分类',
      city: '全部城市',
      name: '全部企业'
    },
    loading: true
  },

  onLoad() {
    this.loadData()
  },

  onPullDownRefresh() {
    this.loadData(() => {
      wx.stopPullDownRefresh()
    })
  },

  loadData(cb) {
    wx.request({
      url: app.globalData.apiUrl,
      method: 'GET',
      timeout: 15000,
      success: (res) => {
        if (res.statusCode === 200 && res.data) {
          this.initData(res.data)
        } else {
          this.showToast('数据加载失败')
        }
      },
      fail: () => {
        this.showToast('网络请求失败，请检查域名配置')
      },
      complete: () => {
        if (cb) cb()
      }
    })
  },

  initData(d) {
    const today = d.today || []
    const data = d.data || []

    // 构建筛选项
    const industries = this.buildUniqueOptions(data, 'industry', '全部产业领域')
    const types = this.buildUniqueOptions(data, 'type', '全部事项分类')
    const names = this.buildUniqueOptions(data, 'name', '全部企业')
    const cities = this.buildCityOptions(data)

    this.setData({
      dateLine: (d.date || '') + ' · 今日参阅',
      today,
      data,
      filterOptions: {
        industry: industries,
        type: types,
        city: cities,
        name: names
      },
      loading: false
    })
    this.applyFilters()
  },

  buildUniqueOptions(arr, key, label) {
    const set = new Set()
    arr.forEach(r => {
      if (r[key]) set.add(r[key])
    })
    return [label, ...[...set].sort()]
  },

  buildCityOptions(arr) {
    const set = new Set()
    arr.forEach(r => {
      (r.city || '').split(/[;；,、\/]/).forEach(c => {
        c = c.trim()
        if (c) set.add(c)
      })
    })
    return ['全部城市', ...[...set].sort()]
  },

  // ==================== Tab 切换 ====================
  switchTab(e) {
    const tab = e.currentTarget.dataset.tab
    const isToday = tab === 'today'
    this.setData({
      activeTab: tab,
      topTitle: '无锡市重点关注企业商业动态',
      topSub: isToday
        ? '编制：市城运中心 · 来源：政府官网 / 企业公告 / 权威媒体等'
        : '全量 ' + this.data.data.length + ' 条动态 · 可检索/筛选/下载'
    })
    wx.pageScrollTo({ scrollTop: 0, duration: 200 })
  },

  // ==================== 搜索 ====================
  onSearch(e) {
    this.setData({ searchQuery: e.detail.value })
    this.applyFilters()
  },

  // ==================== 筛选 ====================
  onFilterChange(e) {
    const key = e.currentTarget.dataset.key
    const idx = parseInt(e.detail.value)
    const options = this.data.filterOptions[key]

    this.setData({
      ['filterIndex.' + key]: idx,
      ['filterDisplay.' + key]: options[idx]
    })
    this.applyFilters()
  },

  applyFilters() {
    const { data, searchQuery, filterIndex, filterOptions } = this.data
    const ff = filterIndex.industry > 0 ? filterOptions.industry[filterIndex.industry] : ''
    const ft = filterIndex.type > 0 ? filterOptions.type[filterIndex.type] : ''
    const fc = filterIndex.city > 0 ? filterOptions.city[filterIndex.city] : ''
    const fn = filterIndex.name > 0 ? filterOptions.name[filterIndex.name] : ''
    const q = (searchQuery || '').trim().toLowerCase()

    const filtered = data.filter(r => {
      if (ff && r.industry !== ff) return false
      if (ft && r.type !== ft) return false
      if (fn && r.name !== fn) return false
      if (fc && !(r.city || '').includes(fc)) return false
      if (q) {
        const blob = (r.name + r.field + r.type + r.desc + r.city + r.source).toLowerCase()
        if (!blob.includes(q)) return false
      }
      return true
    })

    this.setData({ filteredData: filtered, filteredCount: filtered.length })
  },

  resetFilters() {
    this.setData({
      searchQuery: '',
      filterIndex: { industry: 0, type: 0, city: 0, name: 0 },
      filterDisplay: {
        industry: '全部产业领域',
        type: '全部事项分类',
        city: '全部城市',
        name: '全部企业'
      }
    })
    this.applyFilters()
  },

  // ==================== 复制链接 ====================
  copyLink(e) {
    const url = e.currentTarget.dataset.url
    if (!url) return
    wx.setClipboardData({
      data: url,
      success: () => {
        wx.showToast({ title: '链接已复制', icon: 'success', duration: 1500 })
      }
    })
  },

  // ==================== 下载 Excel ====================
  downloadExcel() {
    wx.showLoading({ title: '下载中...' })
    wx.downloadFile({
      url: app.globalData.xlsxUrl,
      success: (res) => {
        if (res.statusCode === 200) {
          wx.openDocument({
            filePath: res.tempFilePath,
            fileType: 'xlsx',
            success: () => {},
            fail: () => {
              this.showToast('打开失败，请重试')
            }
          })
        } else {
          this.showToast('下载失败')
        }
      },
      fail: () => {
        this.showToast('下载失败，请检查域名配置')
      },
      complete: () => {
        wx.hideLoading()
      }
    })
  },

  showToast(msg) {
    wx.showToast({ title: msg, icon: 'none', duration: 2500 })
  },

  onShareAppMessage() {
    return {
      title: '无锡重点关注企业商业动态 · 每日参阅',
      path: '/pages/index/index'
    }
  }
})
