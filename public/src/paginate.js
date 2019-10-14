import React from "react";
import "./css/paginate.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

class Paginate extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      record: props.record,
      totalPages: Math.ceil(props.record.data.count / props.record.meta.limit),
      currentPage: props.record.meta.page
    };
  }

  componentDidMount() {}

  componentWillUnmount() {}

  static getDerivedStateFromProps(nextProps, prevState) {
    let count = nextProps.record.data.count || 0;
    return {
      record: nextProps.record,
      totalPages: Math.ceil(count / nextProps.record.meta.limit),
      currentPage: nextProps.record.meta.page
    };
  }

  validatePage(value) {
    // if input is a number or space (allowing for backspace), return value (if 0 change to 1), else current page
    return /^[\d\s]*$/.test(value)
      ? parseInt(value) === 0
        ? 1
        : value
      : this.state.currentPage;
  }

  switchPage({ linkedPage = 0, dir = "selected" } = {}) {
    let { url, page, previous, next } = this.state.record.meta;
    switch (dir) {
      case "selected":
        page = linkedPage;
        url = null; // to be set in DataTable.handleGetRecords()
        break;
      case "previous":
        page = page >= 1 ? page - 1 : 1;
        url = previous ? previous : null;
        break;
      case "next":
        page =
          this.state.totalPages > this.state.record.meta.page
            ? this.state.record.meta.page + 1
            : this.state.record.meta.page;
        url = next ? next : null;
        break;
      default:
        page = linkedPage;
        break;
    }
    let newRecord = JSON.parse(JSON.stringify(this.state.record));
    Object.assign(newRecord.meta, {
      page: page,
      limit: this.state.record.meta.limit
    });
    this.props.handleGetRecords({ record: newRecord, url: url });
    // locally set page state, to prevent delay when quick typing, pending overwrite by new source-of-truth prop
    this.setState({ currentPage: page });
  }

  currentPage() {
    return (
      <React.Fragment>
        <div className={"linkedPage"}>
          <label className={"d-none"}>Current page</label>
          <input
            onKeyDown={e =>
              e.keyCode === 8 ? this.setState({ currentPage: "" }) : null
            }
            onChange={e => {
              this.switchPage({
                linkedPage:
                  parseInt(e.target.value) > 0
                    ? parseInt(e.target.value) <= this.state.totalPages
                      ? parseInt(e.target.value)
                      : this.state.totalPages
                    : 1,
                dir: "selected"
              });
            }}
            value={this.state.currentPage}
            type={"text"}
            className={"form-control input-sm page-input"}
          />
        </div>
      </React.Fragment>
    );
  }

  prevSection = () => {
    return (
      <React.Fragment>
        <li className="page-item">
          <button
            aria-label="previous"
            onClick={() => this.switchPage({ dir: "previous" })}
            className="page-link"
          >
            <span aria-hidden="true">&laquo;</span>
            <span className="sr-only">Previous</span>
          </button>
        </li>
      </React.Fragment>
    );
  };

  nextSection = () => {
    return (
      <React.Fragment>
        <li className="page-item">
          <button
            aria-label="next"
            onClick={() => this.switchPage({ dir: "next" })}
            className="page-link"
          >
            <span aria-hidden="true">&raquo;</span>
            <span className="sr-only">Next</span>
          </button>
        </li>
      </React.Fragment>
    );
  };

  mainSection = () => {
    let pageItemClass;
    let pagerMainSize = this.state.record.meta.pagerMainSize;
    let linkedPage = this.state.record.meta.page;
    let totalPages = isNaN(this.state.totalPages) ? 0 : this.state.totalPages;
    return (
      <React.Fragment>
        {[...Array(totalPages)].map((o, pageIndex) => {
          /* if selected (displayed) page is this list item, add 'active' to class to colour it
                    and remove elements over the max size of displayed list */
          pageIndex + 1 > pagerMainSize
            ? (pageItemClass = "d-none")
            : linkedPage === pageIndex + 1
            ? (pageItemClass = "active page-item")
            : (pageItemClass = "page-item");
          return (
            <li className={pageItemClass} key={pageIndex + 1}>
              <button
                onClick={() =>
                  this.switchPage({
                    linkedPage: pageIndex + 1,
                    dir: "selected"
                  })
                }
                className="page-link"
              >
                {pageIndex + 1}
              </button>
            </li>
          );
        })}
      </React.Fragment>
    );
  };

  endSection = () => {
    let pagerMainSize = this.state.record.meta.pagerMainSize;
    let linkedPage = this.state.record.meta.page;
    let totalPages = this.state.totalPages;
    let numEndEle = this.state.record.meta.pagerEndSize;
    let iterArray = Array.apply(null, { length: numEndEle }); // create array as basis for map in frag to iterate
    return (
      <React.Fragment>
        {iterArray.map((o, c) => {
          let p = iterArray.length - (c + 1); // flip count order
          let page = totalPages - p || 0;
          return (
            <li
              key={p}
              className={
                page > pagerMainSize
                  ? linkedPage === page
                    ? "active page-item"
                    : "page-item"
                  : "d-none"
              }
            >
              <button
                onClick={() =>
                  this.switchPage({ linkedPage: page, dir: "selected" })
                }
                href="#"
                className="page-link"
              >
                {page}
              </button>
            </li>
          );
        })}
      </React.Fragment>
    );
  };

  render() {
    return (
      <div className={"pager"}>
        {this.currentPage()}
        <ul className={"pagination pagination-sm"}>
          {this.prevSection()}
          {this.mainSection()}
          <span className={"splitter"}>
            <FontAwesomeIcon icon={"ellipsis-h"} />
          </span>
          {this.endSection()}
          {this.nextSection()}
        </ul>
      </div>
    );
  }
}

export default Paginate;
