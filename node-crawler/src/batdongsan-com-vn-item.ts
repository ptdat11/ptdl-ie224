export interface CrawledItem {};

export type BatdongsanComVnProperty = "area" | "price" | "frontLength" | "entranceLength" |
    "facingDir" | "balconyDir" | "floor" | "bedroom" | "wc" | "legalStatus" | "furniture";

const propertyNameMap: {[property: string]: BatdongsanComVnProperty} = {};
propertyNameMap["Diện tích"] = "area";
propertyNameMap["Mức giá"] = "price";
propertyNameMap["Mặt tiền"] = "frontLength";
propertyNameMap["Đường vào"] = "entranceLength";
propertyNameMap["Hướng nhà"] = "facingDir";
propertyNameMap["Hướng ban công"] = "balconyDir";
propertyNameMap["Số tầng"] = "floor";
propertyNameMap["Số phòng ngủ"] = "bedroom";
propertyNameMap["Số toilet"] = "wc";
propertyNameMap["Pháp lý"] = "legalStatus";
propertyNameMap["Nội thất"] = "furniture";

export interface BatdongsanVnComItem extends CrawledItem {
    _id: number,
    title: string,
    url: string,
    verified: boolean,
    publishDate: string,
    dueDate: string,
    newsRank: string,
    businessForm: string,
    city: string,
    district: string,
    street: string,
    category: string,
    price: string,
    description: string,
    projectTitle: string,
    projectPriceOnArea: string,
    projectArea: string,
    projectBuildings: number | string,
    projectInvestor: string,
    // IQRDomain: string,
    // IQR_Q1: string,
    // IQR_Q2: string,
    // IQR_Q3: string,
    latitude: number,
    longitude: number,
    area: string,
    frontLength: string,
    entranceLength: string,
    facingDir: string,
    balconyDir: string,
    floor?: number,
    bedroom?: number,
    wc?: number,
    legalStatus: string,
    furniture: string
}

export {propertyNameMap};