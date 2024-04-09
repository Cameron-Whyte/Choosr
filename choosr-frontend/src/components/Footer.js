function Footer({ showFooter }) {
    return (
      <div className={`w-full bg-gray-900 text-white p-6 text-center ${showFooter ? '' : 'footer-hidden'}`}>
        <p className="text-lg">© 2023 Choosr. All rights reserved.</p>
        {/* should probably add tmdb api logo here for credit */}
      </div>
    );
  }
  
  export default Footer;
  
  
  
  