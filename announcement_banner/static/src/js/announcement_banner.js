/** @odoo-module **/

import { Component, onWillStart, useState, markup } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class AnnouncementBanner extends Component {
  static template = "announcement_banner.AnnouncementBanner";

  setup() {
    this.orm = useService("orm");
    this.state = useState({
      announcements: [],
      currentIndex: 0,
      showBanner: false,
      isLoading: true,
    });

    onWillStart(async () => {
      await this.loadAnnouncements();
    });
  }

  async loadAnnouncements() {
    try {
      const announcements = await this.orm.call(
        "announcement.banner",
        "get_active_announcements",
        []
      );

      if (announcements && announcements.length > 0) {
        // Process announcements to wrap message in markup for HTML rendering
        this.state.announcements = announcements.map((announcement) => ({
          ...announcement,
          message: markup(announcement.message), // KEY FIX: Wrap message in markup()
        }));
        this.state.showBanner = true;
      }
    } catch (error) {
      console.error("Error loading announcements:", error);
    } finally {
      this.state.isLoading = false;
    }
  }

  async closeBanner() {
    const currentAnnouncement =
      this.state.announcements[this.state.currentIndex];

    try {
      await this.orm.call("announcement.banner", "mark_as_shown", [
        currentAnnouncement.id,
      ]);
    } catch (error) {
      console.error("Error marking announcement as shown:", error);
    }

    // Move to next announcement or hide banner
    if (this.state.currentIndex < this.state.announcements.length - 1) {
      this.state.currentIndex++;
    } else {
      this.state.showBanner = false;
    }
  }

  async dismissCurrent() {
    // Alternative method to just dismiss current without marking as shown
    if (this.state.currentIndex < this.state.announcements.length - 1) {
      this.state.currentIndex++;
    } else {
      this.state.showBanner = false;
    }
  }

  async markCurrentAsShown() {
    // Mark as shown without closing
    const currentAnnouncement =
      this.state.announcements[this.state.currentIndex];

    try {
      await this.orm.call("announcement.banner", "mark_as_shown", [
        currentAnnouncement.id,
      ]);
    } catch (error) {
      console.error("Error marking announcement as shown:", error);
    }
  }

  nextAnnouncement() {
    if (this.state.currentIndex < this.state.announcements.length - 1) {
      this.state.currentIndex++;
    }
  }

  previousAnnouncement() {
    if (this.state.currentIndex > 0) {
      this.state.currentIndex--;
    }
  }

  get currentAnnouncement() {
    return this.state.announcements[this.state.currentIndex];
  }

  get hasMultipleAnnouncements() {
    return this.state.announcements.length > 1;
  }

  get currentPosition() {
    return `${this.state.currentIndex + 1} / ${
      this.state.announcements.length
    }`;
  }

  get hasPrevious() {
    return this.state.currentIndex > 0;
  }

  get hasNext() {
    return this.state.currentIndex < this.state.announcements.length - 1;
  }
}

// Register the component to be loaded in the backend
registry.category("main_components").add("AnnouncementBanner", {
  Component: AnnouncementBanner,
});
