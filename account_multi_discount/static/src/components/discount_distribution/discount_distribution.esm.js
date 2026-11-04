import {Component, useExternalListener, useRef, useState} from "@odoo/owl";
import {TagsList} from "@web/core/tags_list/tags_list";
import {_t} from "@web/core/l10n/translation";
import {browser} from "@web/core/browser/browser";
import {getActiveHotkey} from "@web/core/hotkeys/hotkey_service";
import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";
import {usePosition} from "@web/core/position/position_hook";
import {useRecordObserver} from "@web/model/relational_model/utils";

const COLORS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11];

export class DiscountDistribution extends Component {
    static template = "account_multi_discount.DiscountDistribution";
    static components = {TagsList};
    static props = {...standardFieldProps};

    setup() {
        this.state = useState({
            showDropdown: false,
            discounts: [],
        });

        this.widgetRef = useRef("discountWidget");
        this.dropdownRef = useRef("discountDropdown");
        this.mainRef = useRef("mainElement");
        usePosition("discountDropdown", () => this.widgetRef.el);

        useRecordObserver((record) => {
            // Sync state if record changes externally
            this._syncFromRecord(record);
        });

        useExternalListener(browser, "click", this.onWindowClick, true);
    }

    // -------------------------------------------------------------------------
    // Getters
    // -------------------------------------------------------------------------

    get value() {
        return this.props.record.data[this.props.name] || [];
    }

    get tags() {
        const discounts = this.value;
        if (!discounts.length) return [];
        return discounts.map((d, i) => ({
            id: i,
            text: `${parseFloat(d.toFixed(2))}%`,
            colorIndex: COLORS[i % COLORS.length],
            onClick: (ev) => this.tagClicked(ev),
        }));
    }

    get aggregatedDiscount() {
        const discounts = this.value;
        if (!discounts.length) return "0";
        let factor = 1.0;
        for (const d of discounts) {
            factor *= 1 - (d || 0) / 100;
        }
        return ((1 - factor) * 100).toFixed(2);
    }

    get hasMultipleDiscounts() {
        return this.value.length > 1;
    }

    get isDropdownOpen() {
        return this.state.showDropdown && Boolean(this.dropdownRef.el);
    }

    get editingRecord() {
        return !this.props.readonly;
    }

    // -------------------------------------------------------------------------
    // Actions
    // -------------------------------------------------------------------------

    addLine() {
        this.state.discounts.push(0);
    }

    deleteLine(index) {
        this.state.discounts.splice(index, 1);
    }

    onDiscountInput(index, ev) {
        const val = parseFloat(ev.target.value);
        this.state.discounts[index] = isNaN(val) ? 0 : val;
    }

    async save() {
        // Filter out zero/empty discounts
        const cleaned = this.state.discounts.filter(
            (d) => d !== null && d !== undefined && d !== 0
        );
        await this.props.record.update({
            [this.props.name]: cleaned.length ? cleaned : false,
        });
    }

    // -------------------------------------------------------------------------
    // Open / Close
    // -------------------------------------------------------------------------

    openDropdown() {
        if (this.props.readonly) return;
        this.state.discounts = [...this.value];
        if (!this.state.discounts.length) {
            this.state.discounts.push(0);
        }
        this.state.showDropdown = true;
    }

    closeDropdown() {
        if (this.isDropdownOpen) {
            this.save();
            this.state.showDropdown = false;
        }
    }

    forceCloseDropdown() {
        this.preventOpen = true;
        this.closeDropdown();
        if (this.mainRef.el) {
            this.mainRef.el.focus();
        }
        this.preventOpen = false;
    }

    tagClicked(ev) {
        if (this.editingRecord && !this.isDropdownOpen) {
            this.openDropdown();
            ev.stopPropagation();
        }
    }

    onMainElementFocus() {
        if (!this.isDropdownOpen && !this.preventOpen) {
            this.openDropdown();
        }
    }

    // -------------------------------------------------------------------------
    // Events
    // -------------------------------------------------------------------------

    onWindowClick(ev) {
        if (
            this.isDropdownOpen &&
            !this.widgetRef.el.contains(ev.target) &&
            !ev.target.isSameNode(ev.target.ownerDocument.documentElement)
        ) {
            this.forceCloseDropdown();
        }
    }

    onWidgetKeydown(ev) {
        if (!this.editingRecord) return;
        const hotkey = getActiveHotkey(ev);
        switch (hotkey) {
            case "escape":
                if (this.isDropdownOpen) {
                    this.forceCloseDropdown();
                    break;
                }
                return;
            case "enter":
                if (this.isDropdownOpen) {
                    this.forceCloseDropdown();
                    break;
                }
                return;
            case "arrowdown":
                if (!this.isDropdownOpen) {
                    this.openDropdown();
                    break;
                }
                return;
            default:
                return;
        }
        ev.preventDefault();
        ev.stopPropagation();
    }

    // -------------------------------------------------------------------------
    // Private
    // -------------------------------------------------------------------------

    _syncFromRecord(record) {
        if (!this.isDropdownOpen) {
            // Only sync when popup is closed — user edits take priority
            const val = record.data[this.props.name] || [];
            this.state.discounts = [...val];
        }
    }
}

export const discountDistribution = {
    component: DiscountDistribution,
    displayName: _t("Discount Distribution"),
    supportedTypes: ["json", "jsonb", "char", "text"],
};

registry.category("fields").add("discount_distribution", discountDistribution);
